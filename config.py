# PATH_PREFIX = "/media/nhphucqt/NHPHUCQT/Research/shrec2024/protein"

# PATH_PREFIX = "/home/nhphucqt/Documents/MyLabs/protein"
PATH_PREFIX = "/root/dataset"

MESH_CONF = {
    "query": {
        "num": 387,
        "type": "queries_bin_dec",
        "save": "queries_states",
        "decimate": "queries_bin_dec"
    },
    "target": {
        "num": 520,
        "type": "targets_bin_dec",
        "save": "targets_states",
        "decimate": "targets_bin_dec"
    }
}

CONF = {
    "n_fibo": 24,
    "n_rot": 16,
    "h_mat_shape": (100, 100)
}

# 0 to 10
RANGE_ID = 0

RANGE_QUERIES = [
    (0, 35),
    (35, 70),
    (70, 105),
    (105, 140),
    (140, 175),
    (175, 210),
    (210, 245),
    (245, 280),
    (280, 315),
    (315, 350),
    (350, 387)
]

RANGE_TARGETS = [
    (0, 47),
    (47, 94),
    (94, 141),
    (141, 188),
    (188, 235),
    (235, 282),
    (282, 329),
    (329, 376),
    (376, 423),
    (423, 470),
    (470, 520)
]