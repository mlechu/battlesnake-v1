# battlesnake-v1

A snake submitted to https://play.battlesnake.com. Derived from the [Python starter project](https://github.com/battlesnakeofficial/starter-snake-python).

Mostly incomplete. Would like to write a C or Rust battlesnake next time for fun.

## project state

server_logic is the backup file in use, where server_logic_not_working is an "upgraded" (but not working) version attempted last-minute. Floodfill implementation is either hanging or taking longer than ~200ms (factoring in $0 server hosting delay of ~300ms).

### addressed in server_logic_not_working
- The eat_map isn't actually used yet; snake just avoids certain death
- refactor food searching– currently eats quite a lot
- there are still some bugs + dumb deaths
- pathfinding to avoid getting trapped; find larger map section to enter

### more ambitious todos
- trap other snakes
- use health information of other snakes
- less greedy/nearsighted. Look beyond 1 square LOL