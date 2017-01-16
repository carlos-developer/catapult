#!/usr/bin/env python
# Copyright 2017 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""
Unit tests for the contents of flag_changer.py.
The test will invoke real devices
"""

import os
import posixpath
import sys
import unittest

if __name__ == '__main__':
  sys.path.append(
      os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', )))

from devil.android import device_test_case
from devil.android import device_utils
from devil.android import flag_changer
from devil.android.sdk import adb_wrapper


_CMDLINE_FILE = 'dummy-command-line'


class FlagChangerTest(device_test_case.DeviceTestCase):

  def setUp(self):
    super(FlagChangerTest, self).setUp()
    self.adb = adb_wrapper.AdbWrapper(self.serial)
    self.adb.WaitForDevice()
    self.device = device_utils.DeviceUtils(
        self.adb, default_timeout=10, default_retries=0)
    # pylint: disable=protected-access
    self.cmdline_path = posixpath.join(flag_changer._CMDLINE_DIR, _CMDLINE_FILE)
    self.cmdline_path_legacy = posixpath.join(
        flag_changer._CMDLINE_DIR_LEGACY, _CMDLINE_FILE)

  def tearDown(self):
    self.device.RemovePath(
        [self.cmdline_path, self.cmdline_path_legacy], force=True, as_root=True)

  def testFlagChanger(self):
    if not self.device.HasRoot():
      self.skipTest('Test needs a rooted device')

    # Write some custom chrome command line flags.
    self.device.WriteFile(
        self.cmdline_path, 'chrome --custom --flags')

    # Write some more flags on a command line file in the legacy location.
    self.device.WriteFile(
        self.cmdline_path_legacy, 'some --stray --flags', as_root=True)
    self.assertTrue(self.device.PathExists(self.cmdline_path_legacy))

    changer = flag_changer.FlagChanger(self.device, _CMDLINE_FILE)

    # Legacy command line file is removed, ensuring Chrome picks up the
    # right file.
    self.assertFalse(self.device.PathExists(self.cmdline_path_legacy))

    changer.ReplaceFlags(['--my', '--new', '--flags'])
    # TODO(perezju): assert that new flags are now set.

    changer.Restore()
    # TODO(perezju): assert that flags are back to --custom --flags.


if __name__ == '__main__':
  unittest.main()
