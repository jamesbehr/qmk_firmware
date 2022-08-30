KEYMAP_FOLDER = keyboards/moonlander/keymaps/jamesbehr

.PHONY: graphics
graphics: $(KEYMAP_FOLDER)/media/0.svg \
	$(KEYMAP_FOLDER)/media/1.svg \
	$(KEYMAP_FOLDER)/media/2.svg \
	$(KEYMAP_FOLDER)/media/3.svg

AUDIO_ENABLE = no
PROGRAMMABLE_BUTTON_ENABLE = yes

$(KEYMAP_FOLDER)/media/%.svg: $(KEYMAP_FOLDER)/keys.json $(KEYMAP_FOLDER)/info.json $(KEYMAP_FOLDER)/draw.py
	python $(KEYMAP_FOLDER)/draw.py --keymap $(KEYMAP_FOLDER)/keys.json --info $(KEYMAP_FOLDER)/info.json --labels $(KEYMAP_FOLDER)/labels.json --layer $* > $@

$(KEYMAP_FOLDER)/info.json:
	qmk info -kb moonlander -km jamesbehr -f json > $@

$(KEYMAP_FOLDER)/keys.json: $(KEYMAP_FOLDER)/keymap.c
	qmk c2json -kb moonlander -km jamesbehr --no-cpp $^ > $@
