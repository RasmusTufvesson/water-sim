# Water sim
Just a little simulation that I made because I can.

It works by creating a grid of cells that count how many water particles are in them. This is then used by each water particle to try and get to a cell with a lower density.

You can also create circles of different sizes that are basically just particles with a size. They are a bit janky and water can get stuck inside them because particles just check adjacent cells.

## Controls

Escape: quit\
Left mouse: drag water or objects\
Right mouse: repel water\
Middle mouse: create water\
Ctrl: Higher mouse force\
Shift: Lower mouse force, lower circle density when spawning\
F: Enable/disable fps counter\
1: Spawn a small circle\
2: Spawn a medium circle\
3: Spawn a large circle