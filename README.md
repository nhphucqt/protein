### Dataset format

```
dataset
|__ queries
|__ targets
```

### Running method

- Go to the `config.py` file and change the `PATH_PREFIX` to the path of the dataset.

```python
PATH_PREFIX = 'path/to/dataset'
```

- Run the `decimate_modifier.py` file to create the decimated dataset.

```bash
python decimate_modifier.py
```

- Run the `prepare_data.py` file to create height tables with different directions and rotations of the 3D meshes.

```bash
python prepare_data.py
```

- Run the `grid_solver.py` file to evaluate the scores of the queries and targets.

```bash
python grid_solver.py
```

- Run the `save_matrix_score.py` file to save the scores in a matrix format.

```bash
python save_matrix_score.py
```

- Run the `restore_complex.py` file to restore the query-target complexes.

```bash
python restore_complex.py
```