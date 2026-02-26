#!/bin/bash

# Script koji dodaje @login_required na sve rute gde već nije dodat

for file in blueprints/lager.py blueprints/config.py blueprints/email_notify.py blueprints/orders.py; do
    echo "Processing $file..."
    
    # Dodaj @login_required nakon svakog @blueprint.route() ako već nije dodata
    awk '
    /@.*_bp\.route\(/ {
        print
        getline
        if ($0 !~ /@login_required/) {
            print "@login_required"
        }
        print
        next
    }
    { print }
    ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
done

echo "Done! All routes now have @login_required decorator."
