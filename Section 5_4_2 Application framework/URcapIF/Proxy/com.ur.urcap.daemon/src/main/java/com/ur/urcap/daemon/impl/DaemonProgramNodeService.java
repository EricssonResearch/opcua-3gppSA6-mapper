package com.ur.urcap.daemon.impl;

import com.ur.urcap.api.contribution.ViewAPIProvider;
import com.ur.urcap.api.contribution.program.ContributionConfiguration;
import com.ur.urcap.api.contribution.program.CreationContext;
import com.ur.urcap.api.contribution.program.ProgramAPIProvider;
import com.ur.urcap.api.contribution.program.swing.SwingProgramNodeService;
import com.ur.urcap.api.domain.SystemAPI;
import com.ur.urcap.api.domain.data.DataModel;

import java.util.Locale;

public class DaemonProgramNodeService implements SwingProgramNodeService<DaemonProgramNodeContribution, DaemonProgramNodeView> {

	public DaemonProgramNodeService() {
	}

	@Override
	public String getId() {
		return "DaemonSwingNode";
	}

	@Override
	public String getTitle(Locale locale) {
		return "Daemon";
	}

	@Override
	public void configureContribution(ContributionConfiguration configuration) {
		configuration.setChildrenAllowed(true);
	}

	@Override
	public DaemonProgramNodeView createView(ViewAPIProvider apiProvider) {
		SystemAPI systemAPI = apiProvider.getSystemAPI();
		Style style = systemAPI.getSoftwareVersion().getMajorVersion() >= 5 ? new V5Style() : new V3Style();
		return new DaemonProgramNodeView(style);
	}

	@Override
	public DaemonProgramNodeContribution createNode(ProgramAPIProvider apiProvider, DaemonProgramNodeView view, DataModel model, CreationContext context) {
		return new DaemonProgramNodeContribution(apiProvider, view, model);
	}

}
