PROJECT = wallpaper-changer
PYTHON  = python3

.PHONY: install uninstall service-start service-stop service-restart service-logs clean

install:
	pip install --user -e .

uninstall:
	pip uninstall $(PROJECT) -y

service-install:
	@mkdir -p ~/.config/systemd/user
	@sed 's|{{SCRIPT_DIR}}|$(CURDIR)|' systemd/wallpaper-changer.service > \
		~/.config/systemd/user/wallpaper-changer.service
	systemctl --user daemon-reload
	systemctl --user enable wallpaper-changer
	systemctl --user start wallpaper-changer

service-remove:
	systemctl --user stop wallpaper-changer 2>/dev/null || true
	systemctl --user disable wallpaper-changer 2>/dev/null || true
	rm -f ~/.config/systemd/user/wallpaper-changer.service
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
