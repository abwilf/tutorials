# TODO: need to do this occassionally
api = wandb.Api(overrides={"project": 'wandb_tutorial', "entity": 'socialiq'})
for run in tqdm(api.runs()):
    try:
        dev = run.history()['primtask.f1.dev']
        dev = dev[~dev.isna()].to_numpy()
        test = run.history()['primtask.f1.test']
        test = test[~test.isna()].to_numpy()
        run.summary['best_auxlearn_test_f1'] = test[dev.argmax()]
        run.update()
    except:
        pass