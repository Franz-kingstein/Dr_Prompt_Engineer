import mlflow

mlflow.set_tracking_uri("file:./mlruns")
experiment_name = "Prompt_Generator"

experiment = mlflow.get_experiment_by_name(experiment_name)
if experiment:
    runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"], max_results=5)
    
    if not runs.empty:
        print(f"Latest {len(runs)} runs for experiment '{experiment_name}':")
        for i, row in runs.iterrows():
            print(f"\nRun ID: {row['run_id']}")
            print(f"Status: {row['status']}")
            print(f"Start Time: {row['start_time']}")
            
            # Print parameters
            params = [c for c in runs.columns if c.startswith('params.')]
            print("Parameters:")
            for p in params:
                print(f"  {p.replace('params.', '')}: {row[p]}")
                
            # Print metrics
            metrics = [c for c in runs.columns if c.startswith('metrics.')]
            print("Metrics:")
            for m in metrics:
                print(f"  {m.replace('metrics.', '')}: {row[m]}")
    else:
        print(f"No runs found for experiment '{experiment_name}'.")
else:
    print(f"Experiment '{experiment_name}' not found.")
