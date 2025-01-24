package com.ur.urcap.daemon.impl;

import com.ur.urcap.api.contribution.ViewAPIProvider;
import com.ur.urcap.api.contribution.installation.ContributionConfiguration;
import com.ur.urcap.api.contribution.installation.CreationContext;
import com.ur.urcap.api.contribution.installation.InstallationAPIProvider;
import com.ur.urcap.api.contribution.installation.swing.SwingInstallationNodeService;
import com.ur.urcap.api.domain.SystemAPI;
import com.ur.urcap.api.domain.data.DataModel;

import java.util.Locale;

public class DaemonInstallationNodeService implements SwingInstallationNodeService<DaemonInstallationNodeContribution, DaemonInstallationNodeView> {

	private final DaemonDaemonService daemonService;

	public DaemonInstallationNodeService(DaemonDaemonService daemonService) {
		this.daemonService = daemonService;
	}

	@Override
	public String getTitle(Locale locale) {
		return "Daemon";
	}

	@Override
	public void configureContribution(ContributionConfiguration configuration) {
	}

	@Override
	public DaemonInstallationNodeView createView(ViewAPIProvider apiProvider) {
		SystemAPI systemAPI = apiProvider.getSystemAPI();
		Style style = systemAPI.getSoftwareVersion().getMajorVersion() >= 5 ? new V5Style() : new V3Style();
		return new DaemonInstallationNodeView(style);
	}

	@Override
	public DaemonInstallationNodeContribution createInstallationNode(InstallationAPIProvider apiProvider, DaemonInstallationNodeView view, DataModel model, CreationContext context) {
		return new DaemonInstallationNodeContribution(apiProvider, view, model, daemonService, new XmlRpcDaemonInterface(), context);
	}

}
