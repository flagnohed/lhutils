#ifndef GAME_H_
#define GAME_H_

#include <stdint.h>

typedef enum {
    EVENT_INV,
    EVENT_GOAL,
    EVENT_SHOT,
    EVENT_PENALTY,
    EVENT_INJURY,
    EVENT_PULL_GOALIE,
}   Event_t;

/* Struct containing statistics for each player that participates
 * in at least one event in a game. */
typedef struct {
    char name[256];
    uint8_t shots;
    uint8_t assists;
    uint8_t penalties;
    uint8_t goals_pp;
    uint8_t goals_bp;
    uint8_t goals_es;
}   GamePlayer_t;

typedef struct {
    char name[256];  /* TODO: Check Livehockey max team name length. */
    GamePlayer_t players[32];  /* TODO: 32 is probably overkill, maybe change? */
    unsigned int icetime_distribution;  /* Percentages per line, e.g., 343432, 404020, ... */
    unsigned int grade;
}   Team_t;

int parse_game(const char *fname);

#endif
