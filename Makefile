ifeq ($(commit),)
    commit = commit by make git
endif

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "make git commit=\"comment\""
	@echo "make pull"


.PHONY: git
git:
	git rm --cached -r .
	git add -A .
	git commit -m "$(commit)"
	git push -u origin master

.PHONY: pull
pull:
	git reset --hard HEAD
	git clean -f -d
	git pull
	systemctl restart josien.net
	systemctl status josien.net
