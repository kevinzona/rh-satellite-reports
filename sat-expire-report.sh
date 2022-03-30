#!/usr/bin/env bash
#
# Search for subscriptions that will expire
#

orgName=${1:-blank}
expireDays=${2:-90}
expireSeconds=$( date -d "@$((epoch + 86400*${expireDays}))" +'%s' )
currentSeconds=$( date +'%s' )

if [[ $orgName == "blank" ]]; then
  echo
  echo "Please give an organization name to search."
  echo "The following example will search \"Default Org\" for subs expiring in 90 days"
  echo "Example: $0 \"Default Org\" 90"
  echo
  exit 1
fi

hammer > /dev/null 2>&1 || { echo "Can not find hammer command"; exit 1; }

# Run hammer report
hammer --csv --csv-separator ";" subscription list --organization "${orgName}" | awk -F";" -v OFS=";" '{ print $3,$5,$7,$9 }' | sed -n '1!p' | while read -r entry; do
  OLDIFS=$IFS
  IFS=";"

  echo "$entry" | while read -r name contract support endDate; do
    expDate=$( date -d "$( cut -d ' ' -f1 <<< $endDate )" +'%s' )
    let secondsLeft=${expDate}-${currentSeconds}

    if [ ${secondsLeft} -lt ${expireSeconds} ];then
      echo "$name in contract \"${contract:-Empty Contract}\" is set to expire on $endDate"
    fi
  done

  IFS=$OLDIFS
done
