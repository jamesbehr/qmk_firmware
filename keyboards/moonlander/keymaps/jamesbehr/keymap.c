/* Copyright 2020 ZSA Technology Labs, Inc <@zsa>
 * Copyright 2020 Jack Humbert <jack.humb@gmail.com>
 * Copyright 2020 Christopher Courtney, aka Drashna Jael're  (@drashna) <drashna@live.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */


#include QMK_KEYBOARD_H
#include "version.h"

enum layers {
    BASE,  // default layer
    SYMB,  // symbols
    NUMB,  // numpad
    GUI,   // gui layer
};

enum custom_keycodes {
    VRSN = ML_SAFE_RANGE,
};

// clang-format off
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE] = LAYOUT_moonlander(
        XXXXXXX,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    XXXXXXX,           XXXXXXX, KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    XXXXXXX,
        XXXXXXX,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    XXXXXXX,           XXXXXXX, KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,    XXXXXXX,
        KC_ESC,   KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    XXXXXXX,           XXXXXXX, KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN, XXXXXXX,
        KC_LSFT,  KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,                                KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH, KC_RSFT,
        KC_LCTL,  KC_LGUI, KC_LALT, MO(GUI), MO(SYMB),         PB_1,              PB_2,             MO(NUMB), MO(GUI),KC_RALT, KC_RGUI, KC_RCTL,
                                             KC_SPC,  KC_BSPC, KC_LALT,           KC_RSFT, KC_TAB,  KC_ENT
    ),

    [SYMB] = LAYOUT_moonlander(
        VRSN,    KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,             KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,   _______,
        _______, XXXXXXX, KC_PLUS, KC_LCBR, KC_RCBR, KC_CIRC, _______,           _______, KC_TILD, KC_GRV,  KC_HASH, KC_EXLM, XXXXXXX,  _______,
        _______, KC_EQL,  KC_MINS, KC_LPRN, KC_RPRN, KC_AT,   _______,           _______, KC_PIPE, KC_UNDS, KC_DQUO, KC_QUOT, KC_COLN,  _______,
        _______, KC_PERC, KC_ASTR, KC_LBRC, KC_RBRC, KC_DLR,                              KC_AMPR, KC_BSLS, KC_LABK, KC_RABK, KC_QUES,  _______,
        _______, _______, _______, _______, _______,          _______,           _______,          _______, _______, _______, _______,  _______,
                                            _______, _______, _______,           _______, _______, _______
    ),

    [NUMB] = LAYOUT_moonlander(
        _______, _______, _______, _______, _______, _______, _______,           _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______,           _______, KC_0,    KC_7,    KC_8,    KC_9,    _______, _______,
        _______, _______, _______, _______, _______, _______, _______,           _______, KC_0,    KC_4,    KC_5,    KC_6,    _______, _______,
        _______, _______, _______, _______, _______, _______,                             KC_0,    KC_1,    KC_2,    KC_3,    _______, _______,
        _______, _______, _______, _______, _______,          _______,           _______,          _______, _______, _______, _______, _______,
                                            _______, _______, _______,           _______, _______, _______
    ),

    [GUI] = LAYOUT_moonlander(
        _______, _______, _______, _______, _______, _______, _______,           _______, _______, _______, _______, _______, EEP_RST, QK_BOOT,
        _______, _______, KC_MS_U, _______, _______, _______, _______,           _______, _______, _______, _______, _______, _______, _______,
        _______, KC_MS_L, KC_MS_D, KC_MS_R, _______, _______, _______,           _______, KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, _______, _______,
        _______, _______, _______, _______, _______, _______,                             _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______,          _______,           _______,          _______, _______, _______, _______, _______,
                                            KC_BTN1, KC_BTN2, KC_BTN3,           _______, _______, _______
    ),
};

void keyboard_post_init_user(void) {
    rgblight_disable();
}

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    if (record->event.pressed) {
        switch (keycode) {
        case VRSN:
            SEND_STRING (QMK_KEYBOARD "/" QMK_KEYMAP " @ " QMK_VERSION);
            return false;
        }
    }
    return true;
}
