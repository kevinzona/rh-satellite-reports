import requests
import urllib3
import getpass
import sys
import argparse

# Suppress SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SatelliteApp:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.base_url = f"https://{self.hostname}/api/v2"
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.verify = False 

    def fetch_users(self):
        """Fetches the list of all users."""
        url = f"{self.base_url}/users"
        try:
            response = self.session.get(url, params={'per_page': 1000})
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            print(f"Error fetching users: {e}", file=sys.stderr)
            return []

    def fetch_user_roles(self, user_id):
        url = f"{self.base_url}/users/{user_id}/roles"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            roles_data = response.json().get('results', [])
            return "; ".join([role.get('name') for role in roles_data])
        except Exception:
            return "Error retrieving roles"

    def fetch_user_orgs(self, user_id):
        url = f"{self.base_url}/users/{user_id}/organizations"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            org_data = response.json().get('results', [])
            return "; ".join([org.get('name') for org in org_data])
        except Exception:
            return "Error retrieving orgs"

    def fetch_user_locs(self, user_id):
        url = f"{self.base_url}/users/{user_id}/locations"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            location_data = response.json().get('results', [])
            return "; ".join([location.get('name') for location in location_data])
        except Exception:
            return "Error retrieving locations"

    def run(self):
        users = self.fetch_users()

        if not users:
            print("No users found or authentication failed.", file=sys.stderr)
            return

        header = "Id,Login,Name,Email,Admin,Disabled,Last login,Authorized by,Email enabled,Effective admin,Locale,Timezone,Description,Default organization,Default location,Roles::1,Locations::1,Organizations::1,Created at,Updated at"
        print(header)

        for u in users:
            user_id = u['id']
            full_name = f"{u.get('firstname', '')} {u.get('lastname', '')}"
            
            role_names = self.fetch_user_roles(user_id)
            org_names = self.fetch_user_orgs(user_id)
            loc_names = self.fetch_user_locs(user_id)
            
            # Added missing comma between user_id and login
            print(f"{user_id},{u['login']},{full_name},{u.get('mail', '')},{u['admin']},{u['disabled']},{u['last_login_on']},{u['auth_source_name']},{u['mail_enabled']},{u['effective_admin']},{u['locale']},{u['timezone']},{u['description']},{u['default_organization']},{u['default_location']},{role_names},{loc_names},{org_names},{u['created_at']},{u['updated_at']}")

def main():
    parser = argparse.ArgumentParser(description="Fetch user info from Red Hat Satellite")
    parser.add_argument("-s", "--satellite", required=True, help="Satellite hostname (e.g. satellite.example.com)")
    parser.add_argument("-u", "--username", required=True, help="Satellite username")
    parser.add_argument("-p", "--password", help="Satellite password (if omitted, you will be prompted)")

    args = parser.parse_args()

    # Securely prompt for password if not provided in arguments
    password = args.password if args.password else getpass.getpass(f"Password for {args.username}: ")

    app = SatelliteApp(args.satellite, args.username, password)
    app.run()

if __name__ == "__main__":
    main()
