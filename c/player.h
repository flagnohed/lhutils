#ifndef PLAYER_H_
#define PLAYER_H_

#include <stdint.h>
#include <stdbool.h>

#define LEN_DIVIDER 30
#define MAX_DAYS 7
#define MAX_WEEKS 13

typedef struct {
    uint8_t day;
    uint8_t week;
}   Date_t;

typedef enum {
    POS_INV,
    POS_G,
    POS_D,
    POS_F,
}   Position_t;

typedef struct {
    uint8_t age;
    unsigned int value;
    unsigned int transfer_list_idx;  /* 1-indexed. 0 is default. */
    unsigned int bid;                /* Current bid or starting bid. */
    bool has_bid;                    /* True if someone has bidded on this player. */
    char *name;
    Date_t bdate;
    Position_t pos;
}   Player_t;

uint8_t get_trainings_left(const Player_t *p, const Date_t cur_date);
void print_value_predictions(const Player_t *p, const Date_t cur_date);

#endif