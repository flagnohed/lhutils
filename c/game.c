#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include "game.h"

#define PATH_GAMES_DIR "input/games/"
#define PATH_GAME_TEST PATH_GAME_TEST "game_test.txt"
#define MAX_LINE_SIZE 256

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

/* FNAME is guaranteed to be null-terminated since it is from argv. */
int parse_game(const char *fname) {
    /* TODO: Maybe make a list of file names to parse and then aggregate stats?
     * if fname is not all then the list should be only one entry but then we
     * can reuse "for each fname in the list, parse game". */

    FILE *fp;
    char line[MAX_LINE_SIZE];
    char fpath[MAX_LINE_SIZE] = "";
    snprintf(fpath, strlen(PATH_GAMES_DIR) + 1, "%s", PATH_GAMES_DIR);
    strcat(fpath, fname);
    if (strcmp(fname, "all") == 0) {
        /* Read all valid game files in PATH_GAMES_DIR and combine stats. */
        printf("Not yet implemented.\n");
        return 1;
    }
    if ((fp = fopen(fpath, "r")) == NULL) {
        printf("Could not open file %s\n", fname);
        return 1;
    }
    while (fgets(line, MAX_LINE_SIZE, fp)) {
        /* TODO: Parse game file. */
        printf("%s\n", line);
    }

    return 0;
}
