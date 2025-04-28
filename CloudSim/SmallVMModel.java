package org.cloudbus.cloudsim.examples;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import org.cloudbus.cloudsim.Cloudlet;
import org.cloudbus.cloudsim.CloudletSchedulerSpaceShared;
import org.cloudbus.cloudsim.Datacenter;
import org.cloudbus.cloudsim.DatacenterBroker;
import org.cloudbus.cloudsim.DatacenterCharacteristics;
import org.cloudbus.cloudsim.Host;
import org.cloudbus.cloudsim.Pe;
import org.cloudbus.cloudsim.UtilizationModel;
import org.cloudbus.cloudsim.UtilizationModelFull;
import org.cloudbus.cloudsim.Vm;
import org.cloudbus.cloudsim.VmAllocationWithSelectionPolicy;
import org.cloudbus.cloudsim.VmSchedulerSpaceShared;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.core.HostEntity;
import org.cloudbus.cloudsim.provisioners.BwProvisionerSimple;
import org.cloudbus.cloudsim.provisioners.PeProvisionerSimple;
import org.cloudbus.cloudsim.provisioners.RamProvisionerSimple;
import org.cloudbus.cloudsim.selectionPolicies.SelectionPolicyFirstFit;

public class SmallVMModel {

	// Configuration
	private static final int SMALL_VM_PES = 1;
	private static final int SMALL_VM_MIPS = 7000;
	private static final int SMALL_VM_RAM = 1024; // 1 GB
	private static final int SMALL_VM_BANDWIDTH = 500;

	// Simulation Constants
	private static final int NUM_DATACENTERS = 2;
	private static final int NUM_HOSTS_PER_DC = 5;
	private static final int HOST_PES = 16;
	private static final int HOST_PE_MIPS = 20000; // MIPS per PE
	private static final int HOST_RAM = 65536; // 64 GB (in MB)
	private static final long HOST_STORAGE = 5 * 1024 * 1024; // 5 TB (in MB)
	private static DatacenterBroker broker;
	private static int hid = 0;

	// Cloud let properties
	private static final int CLOUDLET_LENGTH = 10000;
	private static final int CLOUDLET_PES = 1;
	private static final int CLOUDLET_FILESIZE = 300;
	private static final int CLOUDLET_OUTPUTSIZE = 300;
	private static final int NUM_CLOUDLETS = 1000;

	// main function
	public static void main(String[] args) {

		try {

			CloudSim.init(1, Calendar.getInstance(), false);

			List<Datacenter> datacenters = new ArrayList<>();
			for (int dcId = 0; dcId < NUM_DATACENTERS; dcId++) {
				datacenters.add(createDatacenter("Datacenter_" + dcId));
			}

			broker = new DatacenterBroker("Broker");

			List<Vm> vmList = new ArrayList<>();

			for (int i = 0; i < 20; i++) {
				vmList.add(createVm(i, SMALL_VM_PES, SMALL_VM_MIPS, SMALL_VM_RAM, SMALL_VM_BANDWIDTH));
			}

			broker.submitGuestList(vmList);

			List<Cloudlet> cloudletList = createCloudlets(NUM_CLOUDLETS);

			for (int i = 0; i < cloudletList.size(); i++) {
				// getting particular cloud let
				Cloudlet cloudlet = cloudletList.get(i);
				// assigns using round robin
				// now for only small VMS
				cloudlet.setGuestId(vmList.get(i % 20).getId());
			}

			broker.submitCloudletList(cloudletList);

			CloudSim.startSimulation();

			List<Cloudlet> finishedCloudlets = broker.getCloudletReceivedList();

			CloudSim.stopSimulation();

			printMetrics(finishedCloudlets);

		} catch (Exception e) {
			e.printStackTrace();
		}

	} // main ends here

	private static Datacenter createDatacenter(String name) {
		List<Host> hostList = new ArrayList<>();
		for (int hostId = 0; hostId < NUM_HOSTS_PER_DC; hostId++) {
			List<Pe> peList = new ArrayList<>();
			for (int peId = 0; peId < HOST_PES; peId++) {
				peList.add(new Pe(peId, new PeProvisionerSimple(HOST_PE_MIPS)));
			}
			Host host = new Host(hid++, new RamProvisionerSimple(HOST_RAM), new BwProvisionerSimple(16000),
					HOST_STORAGE, peList, new VmSchedulerSpaceShared(peList));
			hostList.add(host);
		}
		DatacenterCharacteristics characteristics = new DatacenterCharacteristics("x86", "Linux", "Xen", hostList, 10.0,
				0.1, 0.1, 0.1, 0.1);

		try {
			return new Datacenter(name, characteristics,
					new VmAllocationWithSelectionPolicy(hostList, new SelectionPolicyFirstFit<HostEntity>()),
					new ArrayList<>(), 0);
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	} // create data center function ends here

	private static Vm createVm(int id, int pes, int mips, int ram, int bw) {
		return new Vm(id, broker.getId(), mips, pes, ram, bw, 0, "Xen", new CloudletSchedulerSpaceShared());
	} // create VM ends here

	private static List<Cloudlet> createCloudlets(int numCloudlets) {
		UtilizationModel utilizationModel = new UtilizationModelFull();
		List<Cloudlet> cloudletList = new ArrayList<>();
		// cloud lets are created as per the paper
		for (int i = 0; i < numCloudlets; i++) {
			Cloudlet cloudlet = new Cloudlet(i, CLOUDLET_LENGTH, CLOUDLET_PES, CLOUDLET_FILESIZE, CLOUDLET_OUTPUTSIZE,
					utilizationModel, utilizationModel, utilizationModel);
			// assigning broker id is a must
			cloudlet.setUserId(broker.getId());
			cloudletList.add(cloudlet);

		}
		return cloudletList;
	} // create cloud let ends here

	private static void printMetrics(List<Cloudlet> cloudlets) {

		double waitTime = 0, responseTime = 0, turnAroundTime = 0;
		double makespan = cloudlets.get(cloudlets.size() - 1).getExecFinishTime() - cloudlets.get(0).getExecStartTime();

		for (Cloudlet c : cloudlets) {
			waitTime += c.getExecStartTime() - c.getSubmissionTime();
		}

		responseTime = waitTime;

		for (Cloudlet c : cloudlets) {
			responseTime += c.getActualCPUTime();
		}

		for (Cloudlet c : cloudlets) {
			turnAroundTime += c.getExecFinishTime() - c.getSubmissionTime(); 
		}
		turnAroundTime = turnAroundTime / cloudlets.size();

		System.out.println("\n========= Performance Metrics =========");
		System.out.printf("Wait Time: %.2f sec\n", waitTime);
		System.out.printf("Response Time: %.2f sec\n", responseTime);
		System.out.printf("Makespan: %.2f sec\n", makespan);
		System.out.printf("Turn Around Time: %.2f sec\n", turnAroundTime);
	} // print metrics ends here

} // class ends here
