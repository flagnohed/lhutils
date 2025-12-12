#include <dirent.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "game.h"

#define PATH_GAMES_DIR "input/games/"
#define PATH_GAME_TEST PATH_GAME_TEST "game_test.txt"
#define MAX_LINE_SIZE 256

#define IND_DATE "Matchdatum: "
#define IND_ID   "Match-id: "
#define IND_TYPE "Matchtyp: "
#define IND_ICETIME "Istid: "
#define IND_GRADE "Lagbetyg: "

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

static unsigned int parse_icetime_distribution(const char *icetime_str) {
    /* TODO: implement this. */
    return 0;
}

static inline bool starts_with(const char *prefix, const char *str) {
    return strncmp(prefix, str, strlen(prefix)) == 0;
}

/* FNAME is guaranteed to be null-terminated since it is from argv. */
int parse_game(const char *fname) {
    /* TODO: Maybe make a list of file names to parse and then aggregate stats?
     * if fname is not all then the list should be only one entry but then we
     * can reuse "for each fname in the list, parse game". */
    /* TODO: Each line seems to end with newline, strip? */
    FILE *fp;
    char line[MAX_LINE_SIZE];
    char fpath[MAX_LINE_SIZE] = "";
    char *game_date, *game_type;
    int game_id;

    Team_t home = {0};
    Team_t away = {0};

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
        /* General game information. */
        if (starts_with(IND_DATE, line)) {
            game_date = line + strlen(IND_DATE);
        }
        else if (starts_with(IND_ID, line)) {
            game_id = atoi(line + strlen(IND_ID));
        }
        else if (starts_with(IND_TYPE, line)) {
            game_type = line + strlen(IND_TYPE);
        }
        /* Team specific information. */
        else if (starts_with(IND_GRADE, line)) {
            if (home.grade == 0) {
                home.grade = atoi(line + strlen(IND_GRADE));
            }
            else {
                away.grade = atoi(line + strlen(IND_GRADE));
            }
        }
        else if (starts_with(IND_ICETIME, line)) {
            if (home.icetime_distribution == 0) {
                home.icetime_distribution = parse_icetime_distribution(line + strlen(IND_ICETIME));
            }
            else {
                away.icetime_distribution = parse_icetime_distribution(line + strlen(IND_ICETIME));
            }
        }
        else if (starts_with("(", line)) {
            /* Event found. */
        }
        /* TODO: Find a way of parsing team names (only line containing " - "). */
    }

    return 0;
}
