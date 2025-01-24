package com.ur.urcap.daemon.impl;

import com.ur.urcap.api.contribution.DaemonContribution;
import com.ur.urcap.api.contribution.InstallationNodeContribution;
import com.ur.urcap.api.contribution.installation.CreationContext;
import com.ur.urcap.api.contribution.installation.InstallationAPIProvider;
import com.ur.urcap.api.domain.data.DataModel;
import com.ur.urcap.api.domain.script.ScriptWriter;
import com.ur.urcap.api.domain.userinteraction.inputvalidation.InputValidationFactory;
import com.ur.urcap.api.domain.userinteraction.keyboard.KeyboardInputCallback;
import com.ur.urcap.api.domain.userinteraction.keyboard.KeyboardInputFactory;
import com.ur.urcap.api.domain.userinteraction.keyboard.KeyboardTextInput;

import java.awt.EventQueue;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

import com.ur.urcap.daemon.impl.Proxy.Proxy;
import com.ur.urcap.daemon.impl.Proxy.AASClientFunctions.Registration;
import com.ur.urcap.daemon.impl.Proxy.AASClientFunctions.BasicApiFunctions.ApiPutFunction;
import com.ur.urcap.daemon.impl.Proxy.RandomFunctions.ReadFileAsStringWithScanner;

public class DaemonInstallationNodeContribution implements InstallationNodeContribution {
	private static final String POPUP_TITLE_KEY = "popuptitle";
	private static final String XMLRPC_VARIABLE = "daemon_swing";
	private static final String ENABLED_KEY = "enabled";
	private static final String DEFAULT_VALUE = "Daemon";
	private static final long DAEMON_TIME_OUT_NANO_SECONDS = TimeUnit.SECONDS.toNanos(20);
	private static final long RETRY_TIME_TO_WAIT_MILLI_SECONDS = TimeUnit.SECONDS.toMillis(1);

	private final DaemonInstallationNodeView view;
	private final DaemonDaemonService daemonService;
	private final InputValidationFactory inputValidationFactory;
	private final DataModel model;
	private final XmlRpcDaemonInterface daemonStatusMonitor;
	private final KeyboardInputFactory keyboardInputFactory;
	private final ScheduledExecutorService executorService = Executors.newScheduledThreadPool(1);
	private ScheduledFuture<?> scheduleAtFixedRate;

	private Proxy proxy;

	public DaemonInstallationNodeContribution(InstallationAPIProvider apiProvider,
												DaemonInstallationNodeView view,
												DataModel model,
												DaemonDaemonService daemonService,
												XmlRpcDaemonInterface xmlRpcDaemonInterface,
												CreationContext context) {
		keyboardInputFactory = apiProvider.getUserInterfaceAPI().getUserInteraction().getKeyboardInputFactory();
		inputValidationFactory = apiProvider.getUserInterfaceAPI().getUserInteraction().getInputValidationFactory();
		this.view = view;
		this.model = model;
		this.daemonService = daemonService;
		this.daemonStatusMonitor = xmlRpcDaemonInterface;
		if (context.getNodeCreationType() == CreationContext.NodeCreationType.NEW) {
			model.set(POPUP_TITLE_KEY, DEFAULT_VALUE);
		}

		applyDesiredDaemonStatus();

		this.proxy = new Proxy();
	}

	@Override
	public void openView() {
		view.setPopupText(getPopupTitle());
		daemonStatusMonitor.startMonitorThread();

		//UI updates from non-GUI threads must use EventQueue.invokeLater (or SwingUtilities.invokeLater)
		Runnable updateUIRunnable = new Runnable() {
			@Override
			public void run() {
				EventQueue.invokeLater(new Runnable() {
					@Override
					public void run() {
						updateUI();
					}
				});
			}
		};
		if (scheduleAtFixedRate != null) {
			scheduleAtFixedRate.cancel(true);
		}
		scheduleAtFixedRate = executorService.scheduleAtFixedRate(updateUIRunnable, 0, 1, TimeUnit.SECONDS);
	}

	@Override
	public void closeView() {
		if (scheduleAtFixedRate != null) {
			scheduleAtFixedRate.cancel(true);
		}
		daemonStatusMonitor.stopMonitorThread();
	}

	@Override
	public void generateScript(ScriptWriter writer) {

		writer.assign(XMLRPC_VARIABLE, "rpc_factory(\"xmlrpc\", \"" + XmlRpcDaemonInterface.getDaemonUrl() + "\")");
		// Apply the settings to the daemon on program start in the Installation pre-amble
		writer.appendLine(XMLRPC_VARIABLE + ".set_title(\"" + getPopupTitle() + "\")");
		
		
	}

	private void updateUI() {
		DaemonContribution.State state = getDaemonState();

		String text = "";
		switch (state) {
			case RUNNING:
				view.setStartButtonEnabled(false);
				view.setStopButtonEnabled(true);
				text = "Daemon runs";
				break;
			case STOPPED:
				view.setStartButtonEnabled(true);
				view.setStopButtonEnabled(false);
				text = "Daemon stopped";
				break;
			case ERROR:
			default:
				view.setStartButtonEnabled(true);
				view.setStopButtonEnabled(false);
				text = "Daemon failed";
				break;
		}

		view.setStatusLabel(text);
	}

	private void applyDesiredDaemonStatus() {
		new Thread(new Runnable() {
			@Override
			public void run() {
				if (DaemonInstallationNodeContribution.this.isDaemonEnabled()) {
					// Download the daemon settings to the daemon process on initial start for real-time preview purposes
					try {
						DaemonInstallationNodeContribution.this.awaitDaemonRunning();
						daemonStatusMonitor.setTitle(DaemonInstallationNodeContribution.this.getPopupTitle());
					} catch (Exception e) {
						System.err.println("Could not set the title in the daemon process.");
						Thread.currentThread().interrupt();
					}
				} else {
					daemonService.getDaemon().stop();
				}
			}
		}).start();
	}

	private void awaitDaemonRunning() throws InterruptedException {
		daemonService.getDaemon().start();
		long endTime = System.nanoTime() + DAEMON_TIME_OUT_NANO_SECONDS;
		while (System.nanoTime() < endTime) {
			if (daemonStatusMonitor.isDaemonReachable()) {
				break;
			}
			Thread.sleep(RETRY_TIME_TO_WAIT_MILLI_SECONDS);
		}
	}

	public String getPopupTitle() {
		return model.get(POPUP_TITLE_KEY, DEFAULT_VALUE);
	}

	private void setPopupTitle(String title) {
		model.set(POPUP_TITLE_KEY, title);
		// Apply the new setting to the daemon for real-time preview purposes
		// Note this might influence a running program, since the actual state is stored in the daemon.
		try {
			daemonStatusMonitor.setTitle(title);
		} catch (Exception e) {
			System.err.println("Could not set the title in the daemon process.");
		}
	}

	public KeyboardTextInput getInputForTextField() {
		KeyboardTextInput keyboardInput = keyboardInputFactory.createStringKeyboardInput();
		keyboardInput.setErrorValidator(inputValidationFactory.createStringLengthValidator(1, 255));
		keyboardInput.setInitialValue(getPopupTitle());
		return keyboardInput;
	}

	public KeyboardInputCallback<String> getCallbackForTextField() {
		return new KeyboardInputCallback<String>() {
			@Override
			public void onOk(String value) {
				setPopupTitle(value);
				view.setPopupText(value);
			}
		};
	}

	public boolean isPopupTitleSet() {
		return model.isSet(POPUP_TITLE_KEY);
	}

	private DaemonContribution.State getDaemonState() {
		return daemonStatusMonitor.isDaemonReachable() ? daemonService.getDaemon().getState() : DaemonContribution.State.STOPPED;
	}

	private Boolean isDaemonEnabled() {
		return model.get(ENABLED_KEY, true);
	}

	public String getXMLRPCVariable() {
		return XMLRPC_VARIABLE;
	}

	public XmlRpcDaemonInterface getDaemonStatusMonitor() {
		return daemonStatusMonitor;
	}

	public void onStartClick() {
		model.set(ENABLED_KEY, true);
		applyDesiredDaemonStatus();
        
		this.proxy.startAllServicesOfTcpCommunication();
		
	}

	public void onStopClick() {
		model.set(ENABLED_KEY, false);
		applyDesiredDaemonStatus();
		
		this.proxy.stopAllServicesOfTcpCommunication();
	}
}
