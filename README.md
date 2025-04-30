## If you are not showing facts for a guest you can do the following.
### First on the Satallite server
hammer host update --id <id> --build false
### Then on the client
subscription-manager facts --update
