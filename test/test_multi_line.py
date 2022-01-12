import silver_spectacle as ss

ss.DisplayCard("multiLine", dict(
    # name : [ [x1,y1], [x2,y2],  ]
    line1=[
        [ 1,   2   ],
        [ 1.5, 2.3 ],
        [ 2,   3   ],
        [ 5,   5   ],
    ],
    line2=[
        [ 1+1,   2   ],
        [ 1+1.5, 2.3 ],
        [ 1+2,   3   ],
        [ 1+5,   5   ],
    ],
))