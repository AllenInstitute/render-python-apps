# transfer
These are modules for moving data between render instances, particularly useful for moving to a cloud based render if you have small enough data to push through your uplink.

# move_stack
This module simply moves a render stack from one render host to another

# move_pointmatch
This module simply moves a point match collection from one render host to a second render host

# move_stack_and_data_to_s3
This module moves both the metadata and the data from one render host to another (calling the move_stack module in process)
It will effectively serve as an rsync in that it only uploads data to an s3 bucket that isn't already in that bucket.

# transfer_module 
This is a generic module and schema for a transfer process, which now has 2 nested render parameters.

