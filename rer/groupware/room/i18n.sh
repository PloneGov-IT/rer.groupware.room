#!/bin/sh

DOMAIN='rer.groupware.room'

i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --create ${DOMAIN} --merge locales/manual.pot .
i18ndude sync --pot locales/${DOMAIN}.pot locales/*/LC_MESSAGES/${DOMAIN}.po

# for the plone domain
i18ndude rebuild-pot --pot i18n/plone.pot --create plone profiles/default/workflows
i18ndude sync --pot i18n/plone.pot i18n/plone-??.po

# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/${DOMAIN}.mo $lang/LC_MESSAGES/${DOMAIN}.po
    fi
done