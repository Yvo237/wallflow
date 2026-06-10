PROJECT = wallpaper-changer
PYTHON  = python3
WALLPAPER_DIR = $(HOME)/.local/share/$(PROJECT)
BIN_DIR  = $(HOME)/.local/bin
THEME   ?= mixed

.PHONY: install uninstall reinstall service-install service-remove service-start service-stop service-restart service-logs clean

install:
	pipx install .

uninstall:
	-rm -rf $(WALLPAPER_DIR)
	pipx uninstall $(PROJECT)

reinstall: uninstall install

service-install:
	@mkdir -p $(WALLPAPER_DIR)
	@cp -r wallpapers/* $(WALLPAPER_DIR)/
	@mkdir -p $(HOME)/.config/systemd/user
	@sed -e 's|{{BIN}}|$(BIN_DIR)/$(PROJECT)|' \
	     -e 's|{{WALLPAPER_DIR}}|$(WALLPAPER_DIR)|' \
	     -e 's|{{THEME}}|$(THEME)|' \
	     systemd/wallpaper-changer.service > \
	     $(HOME)/.config/systemd/user/wallpaper-changer.service
	systemctl --user daemon-reload
	systemctl --user enable wallpaper-changer
	systemctl --user start wallpaper-changer

service-remove:
	-systemctl --user stop wallpaper-changer 2>/dev/null
	-systemctl --user disable wallpaper-changer 2>/dev/null
	-rm -f $(HOME)/.config/systemd/user/wallpaper-changer.service
	systemctl --user daemon-reload

service-start:
	systemctl --user start wallpaper-changer

service-stop:
	systemctl --user stop wallpaper-changer

service-restart:
	systemctl --user restart wallpaper-changer

service-logs:
	journalctl --user -u wallpaper-changer -f

clean:
	rm -rf *.egg-info __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
