import flor

exp_history = flor.pivot("val_acc", "val_loss")
# Only keep the first experiment
exp_history = exp_history[exp_history["tstamp"] <= exp_history["tstamp"].min()]
# Sort by val_acc
exp_history = exp_history.sort_values("val_acc", ascending=False)
# Sort by val_loss
exp_history = exp_history.sort_values("val_loss", ascending=True)
print(exp_history.head(5))

import os

best_ckpt = exp_history.head(1).to_dict("records")[0]
best_ckpt_path = os.path.join(
    flor.HOMEDIR,
    "obj_store",
    best_ckpt["projid"],
    best_ckpt["tstamp"].isoformat(timespec="seconds"),
    f"model_epochs_{best_ckpt['epochs']}.pth",
)
assert os.path.exists(best_ckpt_path)
print(best_ckpt_path, "exists")

# Copy the best checkpoint to the current directory
import shutil

shutil.copy(best_ckpt_path, "./model.pth")
