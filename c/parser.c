#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parser.h"
#include "player.h"

#define FNAME_TRANSFER_LIST "transfer_list.txt"
#define MAX_LINE_SIZE 256
#define MAX_PLAYER_COUNT 1024

#define IND_CUR_WEEK  "Vecka "  /* Colon intentionally left out because of transfer file format. */
#define IND_POS       "Position: "
#define IND_AGE       "Ålder: "
#define IND_VALUE     "Värde: "
#define IND_START_BID "Utgångsbud: "
#define IND_CUR_BID   "Aktuellt bud: "

static Position_t str_to_pos(const char *pos_str) {
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
        if (*value_str >= '0' && *value_str <= '9') {
            strncat(digits, value_str, 1);
        }
        value_str++;
    }
    return atoi(digits);
}

static void str_to_date(const char *line_ptr, Date_t *date) {
    char week_buf[3] = "";
    while (*line_ptr != '\n' && *line_ptr != '\0') {
        if (isdigit(*line_ptr)) {
            /* Found a digit. Now we need to figure out if this is
                a week or a day. If it is a week it can be two digits. */
            if (date->week == 0) {
                /* Keep adding digits until we find a non-digit. */
                strncat(week_buf, line_ptr, 1);
            }
            else {
                /* Found the player's birth day, which can only be single digit.
                   Date should be parsed fully now. */
                date->day = (uint8_t) *line_ptr - '0';
                break;
            }
        }
        else if (*line_ptr == ',' || (*line_ptr == ' ' && *(line_ptr + 1) == ' ')) {
            /* We are done with parsing the player's birth week OR the current week. */
            date->week = (uint8_t) atoi(week_buf);
        }
        line_ptr++;
    }
}

int parse_transfer_list() {
    /* The transfer list can look one of two ways depending on browser.
       (See transfer_list(_2).txt for comparison) */
    char line[MAX_LINE_SIZE], start_bid_buf[MAX_BUF_LEN_VALUE_STR], age_buf[3], *line_ptr;
    bool is_parsing = false, next_is_name = false;
    unsigned int player_count = 0;
    Player_t *player = NULL, *players[MAX_PLAYER_COUNT];
    FILE *fp;
    size_t i;
    Date_t current_date = {0};

    if ((fp = fopen(FNAME_TRANSFER_LIST, "r")) == NULL) {
        printf("Could not open file %s\n", FNAME_TRANSFER_LIST);
        return 1;
    }
    while (fgets(line, MAX_LINE_SIZE, fp) && player_count < MAX_PLAYER_COUNT) {
        if (isdigit(line[0]) && line[strlen(line) - 2] == '.') {
            /* This is the beginning of a player entry. This means
               that the next line contains the player name. */
            is_parsing = true;
            next_is_name = true;
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
        if (next_is_name) {
            /* Skip the last character as it is a line break. */
            memcpy(player->name, line_ptr, strlen(line_ptr) - 1);
            player->name[strlen(line_ptr) - 1] = '\0';
            next_is_name = false;
        }
        else if (strncmp(line, IND_CUR_WEEK, strlen(IND_CUR_WEEK)) == 0) {
            /* Parse the current date. */
            line_ptr += strlen(IND_CUR_WEEK);
            str_to_date(line_ptr, &current_date);
        }
        else if (strncmp(line, IND_POS, strlen(IND_POS)) == 0) {
            line_ptr += strlen(IND_POS);
            player->pos = str_to_pos(line_ptr);
        }
        else if (strncmp(line, IND_AGE, strlen(IND_AGE)) == 0) {
            line_ptr += strlen(IND_AGE);
            strncpy(age_buf, line_ptr, 2);
            line_ptr += 2;
            player->age = atoi(age_buf);
            str_to_date(line_ptr, &player->bdate);
        }
        else if (strncmp(line, IND_VALUE, strlen(IND_VALUE)) == 0) {
            line_ptr += strlen(IND_VALUE);
            player->value = value_str_to_uint(line_ptr);
        }
        else if (strncmp(line, IND_START_BID, strlen(IND_START_BID)) == 0) {
            /* Save the starting bid into a temp variable. If we later find that
               this player has no current bid, player->bid is set to the starting bid. */
            line_ptr += strlen(IND_START_BID);
            strncpy(start_bid_buf, line_ptr, MAX_BUF_LEN_VALUE_STR - 1);
        }
        else if (strncmp(line, IND_CUR_BID, strlen(IND_CUR_BID)) == 0) {
            /* If the next character is '-', no one has placed a bid on this player yet.
               If it is a digit, we have encountered a bid (in "pretty format",
               e.g. 3 500 000 kr). */
            line_ptr += strlen(IND_CUR_BID);
            player->bid = value_str_to_uint(*line_ptr == '-' ? start_bid_buf : line_ptr);

            /* We are done with the current player here.
               Add it to players list and continue. */
            players[player_count++] = player;
            is_parsing = false;
        }
    }
    fclose(fp);
    for (i = 0; i < player_count; i++) {
        print_value_predictions(players[i], current_date);
    }
    return 0;
}