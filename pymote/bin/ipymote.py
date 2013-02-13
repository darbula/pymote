WIN_SOURCE="""
@echo off
if NOT "%PYMOTE_ENV%" == "" ( call %PYMOTE_ENV%\Scripts\\activate.bat )
ipython --pylab=qt --profile=pymote
"""
def start_ipymote():
    import os, sys
    if sys.platform.startswith("win32"):
        try:
            os.environ['VIRTUAL_ENV'] = os.environ['PYMOTE_ENV']
            os.environ['IPYTHONDIR'] = os.path.join(os.environ['PYMOTE_ENV'],'.ipython')
        except KeyError:
            pass
        
        from IPython.frontend.terminal.ipapp import TerminalIPythonApp
        app = TerminalIPythonApp.instance()
        app.initialize(argv=['--profile=pymote'])#
        app.start()

        """
        import IPython
        ipythondir = IPython.utils.path.get_ipython_dir()
        profiledir = os.path.join(ipythondir, 'profile_pymote')
        
        from IPython.config.loader import PyFileConfigLoader
        cl = PyFileConfigLoader('ipython_config.py',path=profiledir)
        cfg = cl.load_config()
        """
        
        """
        from IPython.config.loader import Config
        cfg = Config()
        cfg.InteractiveShellEmbed.prompt_in1 = "pymote In [\\#]> "
        cfg.InteractiveShellEmbed.prompt_out = "pymote Out [\\#]: "
        cfg.InteractiveShellEmbed.profile = 'pymote'
        """
       
        """
        # directly open the shell
        IPython.embed(config=cfg)#, user_ns=namespace, banner2=banner)
        """
        
        """
        # or get shell object and open it later
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        shell = InteractiveShellEmbed(config=cfg)#, user_ns=namespace, banner2=banner)
        shell.user_ns = {}
        shell()
        """
        
        """
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        InteractiveShellEmbed()(argv=["--profile=pymote"])
        """
        
        """
        if not os.path.exists('pymote.bat'):
            with open("pymote.bat","w") as f:
                f.write(WIN_SOURCE)
        os.startfile("pymote.bat")
        """
        #TODO: start ipython properly - virtualenv sys.path and profile loading should be resolved
        """
        from pkg_resources import load_entry_point
        load_entry_point('ipython', 'console_scripts', 'ipython')()
        """
    
    #TODO: support other platforms
    #elif sys.platform.startswith("linux2"):
    #elif sys.platform.startswith("darwin"):
