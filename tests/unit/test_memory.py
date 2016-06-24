import pytest
from progressbar import ProgressBar
from margaritashotgun.memory import Memory, OutputDestinations
from margaritashotgun.exceptions import *


def test_output_destination_enum():
    assert OutputDestinations.local.value == "local"
    assert OutputDestinations.s3.value == "s3"
    with pytest.raises(AttributeError):
        OutputDestinations.onedrive

def test_init():
    mem = Memory('app01.example.com', 1073741824)

def test_progress():
    mem = Memory('app01.example.com', 1073741824, progressbar=True)
    mem.bar = ProgressBar(widgets=mem.widgets,
                          maxval=mem.max_size).start()
    mem.transfered = 536870912
    mem.update_progress()
    mem.transfered = 2147483648
    mem.update_progress()
    mem.update_progress(complete=True)

    mem = Memory('app02.example.com', 1073741824, progressbar=False)
    mem.bar = ProgressBar(widgets=mem.widgets,
                          maxval=mem.max_size).start()
    mem.transfered = 536870912
    mem.update_progress()
    mem.transfered = 2147483648
    mem.update_progress()
    mem.update_progress(complete=True)

def test_cleanup():
    mem = Memory('app01.example.com', 1073741824, progressbar=True)
    mem.cleanup()
