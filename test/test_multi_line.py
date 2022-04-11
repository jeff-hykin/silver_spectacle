import silver_spectacle as ss

card = ss.DisplayCard("multiLine", dict(
    # name : [ [x1,y1], [x2,y2],  ]
    Line1Name=[
        [ 1,   2   ],
        [ 1.5, 2.3 ],
        [ 2,   3   ],
        [ 5,   5   ],
    ],
    Line2Name=[
        [ 1+1,   2   ],
        [ 1+1.5, 2.3 ],
        [ 1+2,   3   ],
        [ 1+5,   5   ],
    ],
))

# Live update
card.send(dict(
    Line1Name=[
        [ 1,   2   ],
        [ 1.5, 2.3 ],
        [ 2,   3   ],
        [ 5,   5   ],
    ],
    Line2Name=[
        [ 1+1,   2   ],
        [ 1+1.5, 2.3 ],
        [ 1+2,   3   ],
        [ 1+5,   5   ],
    ],
))