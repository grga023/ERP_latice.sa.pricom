#!/bin/bash
# Master refactoring script: Serbian → English in all HTML templates and JS

WORKSPACE="/mnt/d/DSUsers/uif80506/Faks/ERP_latice.sa.pricom"
cd "$WORKSPACE"

echo "🔄 Refactoring HTML templates and JavaScript..."

# Replace Serbian route function names
find templates -name "*.html" -exec sed -i \
  -e "s|/kreiranje|/create|g" \
  -e "s|/porudzbenice|/new-orders|g" \
  -e "s|/realizovano|/realized|g" \
  -e "s|/za-dostavu|/for-delivery|g" \
  -e "s|/lager|/inventory|g" \
  -e "s|kupac|customer|g" \
  -e "s|naziv|name|g" \
  -e "s|cena|price|g" \
  -e "s|placeno|paid|g" \
  -e "s|kolicina|quantity|g" \
  -e "s|boja|color|g" \
  -e "s|opis|description|g" \
  -e "s|slika|image|g" \
  -e "s|lokacija|location|g" \
  -e "s|datum|date|g" \
  -e "s|/api/lager|/api/inventory|g" \
  {} \;

echo "✓ Template files refactored"

# Rename template files
mv templates/kreiranje.html templates/create_order.html 2>/dev/null || echo "- create_order.html already exists"
mv templates/porudzbenice.html templates/new_orders.html 2>/dev/null || echo "- new_orders.html already exists"
mv templates/realizovano.html templates/realized.html 2>/dev/null || echo "- realized.html already exists"
mv templates/za_dostavu.html templates/for_delivery.html 2>/dev/null || echo "- for_delivery.html already exists"
mv templates/lager.html templates/inventory.html 2>/dev/null || echo "- inventory.html already exists"

echo "✓ Template files renamed"

# Find and list remaining Serbian identifiers for manual review
echo ""
echo "📋 Remaining Serbian identifiers (for manual review):"
grep -r "kupac\|naziv\|cena\|placeno\|kolicina\|boja\|opis\|slika\|lokacija\|datum" templates/ static/ --include="*.html" --include="*.js" 2>/dev/null | wc -l || echo "0"

echo "✅ Template refactoring complete!"
