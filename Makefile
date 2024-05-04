.PHONY: potfiles xgettext

potfiles:
	find ./ -not -path '*/.*' -type f -name "*.in" | sort > po/POTFILES
	echo "" >> po/POTFILES
	find ./ -not -path '*/.*' -type f -name "*.ui" -exec grep -l "translatable=\"yes\"" {} \; | sort >> po/POTFILES
	echo "" >> po/POTFILES
	find ./ -not -path '*/.*' -type f -name "*.py" -exec grep -l "_(\"" {} \; | sort >> po/POTFILES

xgettext:
	xgettext --files-from=po/POTFILES --output=po/dev.geopjr.Calligraphy.pot --from-code=UTF-8 --add-comments --keyword=_ --keyword=C_:1c,2
