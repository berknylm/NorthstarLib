#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

"""
Configuration management for NorthstarLib CLI
Handles file paths and settings across different platforms
"""

import json
import os
import platform
from pathlib import Path

__author__ = 'Yeniay RD'
__all__ = ['NorthConfig']


class NorthConfig:
    """North Configuration Manager for CLI settings"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.links_file = self.config_dir / "links.json"
        self.daemon_file = self.config_dir / "daemon.json"
        
        # Create config directory
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_config_dir(self):
        """Get config directory based on OS"""
        if platform.system() == "Windows":
            base = os.getenv('APPDATA', os.path.expanduser('~'))
            return Path(base) / "NorthstarCLI"
        else:
            base = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            return Path(base) / "northstar"
    
    def load_links(self):
        """Load linked agent IDs"""
        if not self.links_file.exists():
            return []
        try:
            with open(self.links_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_links(self, agent_ids):
        """Save linked agent IDs"""
        try:
            with open(self.links_file, 'w') as f:
                json.dump(sorted(set(str(id) for id in agent_ids)), f, indent=2)
        except Exception as e:
            raise Exception(f"Could not save links: {e}")
    
    def load_daemon_info(self):
        """Load daemon connection info"""
        if not self.daemon_file.exists():
            return "127.0.0.1", 7777
        
        try:
            with open(self.daemon_file, 'r') as f:
                data = json.load(f)
                return data.get("host", "127.0.0.1"), data.get("port", 7777)
        except:
            return "127.0.0.1", 7777
    
    def save_daemon_info(self, host, port):
        """Save daemon connection info"""
        try:
            with open(self.daemon_file, 'w') as f:
                json.dump({"host": host, "port": port}, f, indent=2)
        except Exception as e:
            raise Exception(f"Could not save daemon info: {e}")
    
    def remove_daemon_info(self):
        """Remove daemon connection info file"""
        try:
            if self.daemon_file.exists():
                self.daemon_file.unlink()
        except:
            pass  # Ignore errors when cleaning up