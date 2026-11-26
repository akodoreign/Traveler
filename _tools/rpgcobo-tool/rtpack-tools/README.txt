Traveler pack cleanup (Windows, Python 3.12 or newer)

Close the game and coordinate with anyone editing this installation first.
From the game folder, run:

py -3 rtpack-tools\rt_pack_cutover.py prepare .
py -3 rtpack-tools\rt_pack_cutover.py apply . TRANSACTION_ID
py -3 rtpack-tools\rt_pack_cutover.py seal . TRANSACTION_ID

The prepare command prints the transaction ID. Apply moves only verified
duplicate loose assets to quarantine. Seal is a separate choice that frees
disk space; retain the transaction and its referenced pack generation.
To restore, close the game and run:

py -3 rtpack-tools\rt_pack_cutover.py restore . TRANSACTION_ID

Restore never overwrites existing files. Do not remove the retained pack
generation; sealed files need it for recovery.
