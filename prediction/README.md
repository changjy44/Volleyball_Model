# Using Prediction

- Data is stored in `data` folder, while data sorted by date is in `data_sorted` folder.
- For predictions, `base` is for base model, `base_1` for base optimized model, `sliding_window` for sliding window model `sliding_window_1` for sliding window optimized model, `form` for form analysis model.
- `pc1` is for ML base model, `pc2` for half model, `pf1` for half blocking model, `pf2` for removed error model.
- `python` is for python simulator. Running `engine.py` directly should be sufficient

## Run Models and PAT

1. Ensure that you have PAT installed in system
2. In each prediction folder, run `predict_ml.py` to preprocess the matches for analysis
3. Run `python predict_ml.py 1` to run PAT, ensuring that the args correspond to the PAT [executable](https://pat.comp.nus.edu.sg/resources/OnlineHelp/htm/scr/2%20Getting%20Started/2.1%20Installation.htm) in your system. This should create an `output.txt` in each folder.
4. Use `run_scripts.ps1` to batch predictions together
5. Run `analyse_result.py` to see prediction results.
6. Run `check_predictions.py` to see loss results.
7. For ML models, run `check_predictions.py` within the `ml_predictions` folder to see loss results.

## Disclaimer

- Everything was done for the purposes for FYP. The models may not work as intended, slight modifications may be needed. Please compare to the report for any differences in results.
