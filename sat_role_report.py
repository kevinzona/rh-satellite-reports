import requests
import urllib3
import getpass
import sys
import argparse

# Suppress SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SatelliteRoleApp:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.base_url = f"https://{self.hostname}/api/v2"
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.verify = False 

    def fetch_roles(self):
        """Fetches the list of all roles."""
        url = f"{self.base_url}/roles"
        try:
            # Paging to ensure we get all roles
            response = self.session.get(url, params={'per_page': 1000})
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            print(f"Error fetching roles: {e}", file=sys.stderr)
            return []

    def fetch_role_filters(self, role_id):
        """Fetches filters associated with a specific role."""
        url = f"{self.base_url}/roles/{role_id}"
        try:
            response = self.session.get(url, params={'per_page': 1000})
            response.raise_for_status()
            filter_data = response.json().get('filters', [])
            # Formatting as 'Resource: Verb' (e.g., 'Hosts: view_hosts')
            return "; ".join([f"{f.get('resource_type')}" for f in filter_data]).replace(",", ";")
        except Exception:
            return "Error retrieving filters"

    def fetch_role_users(self, role_id):
        """Fetches users assigned to this specific role."""
        # Note: We filter the users endpoint by the role_id
        url = f"{self.base_url}/users"
        try:
            response = self.session.get(url, params={'search': f'role = "{role_id}"'})
            response.raise_for_status()
            user_data = response.json().get('results', [])
            return "; ".join([u.get('login') for u in user_data])
        except Exception:
            return "Error retrieving users"

    def run(self):
        roles = self.fetch_roles()

        if not roles:
            print("No roles found or authentication failed.", file=sys.stderr)
            return

        # CSV Header
        header = "Id,Name,Builtin,Description,Role Filters"
        print(header)

        for r in roles:
            role_id = r['id']
            role_name = r.get('name', '')
            is_builtin = r.get('builtin')
            r_desc = r.get('description', "None")
            r_convert = r_desc.replace("\n", " " ).replace(",", ";")
            role_desc = " ".join(r_convert.split())
            
            # Fetch relational data
            user_list = self.fetch_role_users(role_id)
            f_data = self.fetch_role_filters(role_id)
            f_convert = f_data.replace(",", ";")
            filters_list = " ".join(f_convert.split())
            
            # Print CSV Row
            print(f"{role_id},{role_name},{is_builtin},{role_desc},{filters_list}")

def main():
    parser = argparse.ArgumentParser(description="Fetch Role and Permission info from Red Hat Satellite")
    parser.add_argument("-s", "--satellite", required=True, help="Satellite hostname (e.g. satellite.example.com)")
    parser.add_argument("-u", "--username", required=True, help="Satellite username")
    parser.add_argument("-p", "--password", help="Satellite password (if omitted, you will be prompted)")

    args = parser.parse_args()

    # Securely prompt for password if not provided in arguments
    password = args.password if args.password else getpass.getpass(f"Password for {args.username}: ")

    app = SatelliteRoleApp(args.satellite, args.username, password)
    app.run()

if __name__ == "__main__":
    main()
