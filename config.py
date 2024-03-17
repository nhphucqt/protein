# PATH_PREFIX = "/media/nhphucqt/NHPHUCQT/Research/shrec2024/protein"

PATH_PREFIX = "/home/nhphucqt/Documents/MyLabs/protein"

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