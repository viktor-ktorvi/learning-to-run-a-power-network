# Scripts

This [folder](.) is dedicated to scripts, whether `python`, `bash` or `sbatch`.

Generally, scripts are more for standalone processes or exploring things.

A good rule of thumb is, **if you are executing a python file directly with the python
executable in command line format, it belongs here**.

ex.

```python3 scripts/some_script.py```

Once a script is more mature, it should be generalized and integrated into the package
itself.

## Scripts

List of scripts with their descriptions

| Scripts                           | Description                                                                                                                                                                                               |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `scripts/example_script.py`       | An example script that uses a hydra config and (unrelatedly) prints 'Hello world' : `python3 -m scripts.example_script`                                                                                   |
| `scripts/positional_encodings.py` | Visualizing some graph positional encodings, e.g., Laplacian positional encodings : `python3 -m scripts.positional_encodings positional_encodings.num_components=3 environment.name=l2rpn_case14_sandbox` |
