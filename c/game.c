#include <stdio.h>
#include "game.h"

#define PATH_GAMES_DIR "input/games/"
#define PATH_GAME_TEST PATH_GAME_TEST "game_test.txt"

/* Translates icetime_distribution to its corresponding icetime string (ABCABC...).
 * The last 5 characters of the returned string are for sudden death. */
static const char *get_icetime_str(unsigned int icetime_distribution) {
    switch (icetime_distribution) {
        case 343432:
            return "ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCAB";
        case 404020:
            return "ABABCABABCABABCABABCABABCABABCABABCABABCABABCABABCABABCABABCABABC";
        case 403525:
            return "ABABCABABCACABCABABCABABCACABCABABCABABCACABCABABCABABCABABCABABC";
        case 403030:
            return "ABCABCABACABCABCABCAABCABCABACABCABCABCAABCABCABACABCABCABCAABCAB";
        case 453520:
            return "ABABCACABCABABCABABAABABCACABCABABCABABAABABCACABCABABCABABAABABC";
        case 454015:
            return "ABABCABABCABABCABABAABABCABABCABABCABABAABABCABABCABABCABABAABABC";
        default:
            printf("Invalid icetime distribution: %d\n", icetime_distribution);
            return NULL;
    }
}

int parse_game(void) {
    printf("parse_game()\n");
    return 0;
}
