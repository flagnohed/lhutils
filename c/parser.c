#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parser.h"
#include "player.h"

#define FNAME_TRANSFER_LIST "transfer_list.txt"
#define MAX_LINE_SIZE 256
#define MAX_PLAYER_COUNT 1024

Position_t str_to_pos(const char *pos_str) {
    if (strcmp(pos_str, "Forward\n") == 0) { return POS_F; }
    if (strcmp(pos_str, "Back\n") == 0)    { return POS_D; }
    if (strcmp(pos_str, "Målvakt\n") == 0) { return POS_G; }
    return POS_INV;
}

/* Takes a string like for example "13 370 000 kr" and
   converts it to an unsigned int, like 13370000. */
static unsigned int value_str_to_uint(const char *value_str) {
    char digits[MAX_LINE_SIZE] = "";
    while (*value_str != '\0') {
        if (*value_str >= '0' || *value_str <= '9') {
            strncat(digits, value_str, 1);
        }
        value_str++;
    }
    return atoi(digits);
}

/* The transfer list can look one of two ways depending on browser.
       TODO: implement parser for other browsers than firefox.
       (See transfer_list{_2}.txt for comparison) */
void parse_transfer_list() {
    FILE *fp;
    char line[MAX_LINE_SIZE], *line_ptr, age_buf[3], week_buf[3] = "";
    bool is_parsing = false;
    unsigned int player_count = 0;
    Player_t *player = NULL;
    Player_t *players[MAX_PLAYER_COUNT];

    if ((fp = fopen(FNAME_TRANSFER_LIST, "r")) == NULL) {
        printf("error: could not open file %s\n", FNAME_TRANSFER_LIST);
        return;
    }
    while (fgets(line, MAX_LINE_SIZE, fp) && player_count < MAX_PLAYER_COUNT) {
        /* Last char of every line is \n */
        if (line[0] >= '0' && line[0] <= '9' && line[strlen(line) - 2] == '.') {
            /* This is the beginning of a player entry. This means
               that the next line contains the player name. */
            is_parsing = true;
            player = malloc(sizeof(Player_t));
            continue;
        }
        if (!is_parsing) {
            /* Skip these lines, nothing interesting here. */
            continue;
        }
        line_ptr = &line[0];
        /* Using strlen instead of sizeof on the string literal since
           we want to check if line starts with this string, not equals entirely. */
        if (strncmp(line, "Position: ", strlen("Position: ")) == 0) {
            line_ptr += strlen("Position: ");
            player->pos = str_to_pos(line_ptr);
        }
        else if (strncmp(line, "Ålder: ", strlen("Ålder: ")) == 0) {
            line_ptr += strlen("Ålder: ");
            strncpy(age_buf, line_ptr, 2);
            player->age = atoi(age_buf);
            while (*line_ptr != '\n' && *line_ptr != '\0') {
                if (*line_ptr >= '0' && *line_ptr <= '9') {
                    /* Found a digit. Now we need to figure out if this is
                       a week or a day. If it is a week it can be two digits. */
                    if (player->bdate.week == 0) {
                        /* Keep adding digits until we find a comma. */
                        strncat(week_buf, line_ptr, 1);
                    }
                    else {
                        /* Found the player's birth day, which can only be single digit. */
                        player->bdate.day = *line_ptr - '0';
                        break;
                    }
                }
                else if (*line_ptr == ',') {
                    /* We are done with parsing the player's birth week. */
                    player->bdate.week = atoi(week_buf);
                }
            }
        }
        else if (strncmp(line, "Värde: ", strlen("Värde: ")) == 0) {
            line_ptr += strlen("Värde: ");
            player->value = value_str_to_uint(line_ptr);
        }
        else if (strncmp(line, "Utgångsbud: ", strlen("Utgångsbud: ")) == 0) {
            /* Save the starting bid into a temp variable. If we later find that
               this player has no current bid, player->bid is set to the starting bid. */
        }
        else if (strncmp(line, "Aktuellt bud: ", strlen("Aktuellt bud: ")) == 0) {
            /* If the next character is '-', no one has placed a bid on this player yet.
               If it is a digit, we have encountered a bid (in "pretty format",
               e.g. 3 500 000 kr). */

            /* We are done with the current player here. Add it to players list and continue. */
        }
    }
    fclose(fp);
}