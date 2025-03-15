package com.miniproject.cloudsim;

//package org.cloudbus.cloudsim;

//import org.cloudbus.cloudsim.core.CloudSim;
//import org.cloudbus.cloudsim.provisioners.BwProvisionerSimple;
//import org.cloudbus.cloudsim.provisioners.PeProvisionerSimple;
//import org.cloudbus.cloudsim.provisioners.RamProvisionerSimple;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import org.cloudbus.cloudsim.Cloudlet;
import org.cloudbus.cloudsim.CloudletSchedulerTimeShared;
import org.cloudbus.cloudsim.Datacenter;
import org.cloudbus.cloudsim.DatacenterBroker;
import org.cloudbus.cloudsim.DatacenterCharacteristics;
import org.cloudbus.cloudsim.Host;
import org.cloudbus.cloudsim.Pe;
import org.cloudbus.cloudsim.UtilizationModel;
import org.cloudbus.cloudsim.UtilizationModelFull;
import org.cloudbus.cloudsim.Vm;
import org.cloudbus.cloudsim.VmAllocationPolicySimple;
import org.cloudbus.cloudsim.VmAllocationWithSelectionPolicy;
import org.cloudbus.cloudsim.VmSchedulerSpaceShared;
import org.cloudbus.cloudsim.VmSchedulerTimeShared;
import org.cloudbus.cloudsim.VmSchedulerTimeSharedOverSubscription;
import org.cloudbus.cloudsim.EX.VmSchedulerWithIndependentPes;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.lists.HostList;
import org.cloudbus.cloudsim.provisioners.BwProvisionerSimple;
import org.cloudbus.cloudsim.provisioners.PeProvisionerSimple;
import org.cloudbus.cloudsim.provisioners.RamProvisionerSimple;
import org.cloudbus.cloudsim.selectionPolicies.SelectionPolicy;
import org.cloudbus.cloudsim.selectionPolicies.SelectionPolicyFirstFit;
import org.cloudbus.cloudsim.selectionPolicies.SelectionPolicyRandomSelection;

public class Main {
    // Simulation constants
    private static final int NUM_DATACENTERS = 2;
    private static final int NUM_HOSTS_PER_DC = 10;
    private static final int HOST_PES = 16;
    private static final int HOST_PE_MIPS = 20000; // MIPS per PE
    private static final int HOST_RAM = 65536; // 64 GB (in MB)
    private static final long HOST_STORAGE = 5 * 1024 * 1024; // 5 TB (in MB)
    private static DatacenterBroker broker;
    private static int hid = 0;

    // VM types (from Table 5)
    private static final int SMALL_VM_PES = 1;
    private static final int SMALL_VM_MIPS = 7000;
    private static final int SMALL_VM_RAM = 1024; // 1 GB
    private static final int SMALL_VM_BANDWIDTH = 500; 
    
    private static final int MEDIUM_VM_PES = 1;
    private static final int MEDIUM_VM_MIPS = 20000;
    private static final int MEDIUM_VM_RAM = 4096; // 4 GB
    private static final int MEDIUM_VM_BANDWIDTH = 1000;
    
    private static final int LARGE_VM_PES = 2;
    private static final int LARGE_VM_MIPS = 40000;
    private static final int LARGE_VM_RAM = 8192; // 8 GB
    private static final int LARGE_VM_BANDWIDTH = 2000;

    // Cloudlet properties (from Table 6)
    private static final int CLOUDLET_LENGTH = 10000;
    private static final int CLOUDLET_PES = 1;
    private static final int CLOUDLET_FILESIZE = 300;
    private static final int CLOUDLET_OUTPUTSIZE = 300;

    public static void main(String[] args) {
        try {
            CloudSim.init(1, Calendar.getInstance(), false);

            // Create datacenters with hosts
            List<Datacenter> datacenters = new ArrayList<>();
            for (int dcId = 0; dcId < NUM_DATACENTERS; dcId++) {
                datacenters.add(createDatacenter("Datacenter_" + dcId));
            }

            broker = new DatacenterBroker("Broker");

            // Create mixed VM types (adjust ratios as needed)
            List<Vm> vmList = new ArrayList<>();
//            int vmsPerType = 100; // Example: 50 small, 50 medium, 50 large
//            int totalVms = 88;
//            for (int i = 0; i < totalVms; i+=1) {
//                vmList.add(createVm(i, SMALL_VM_PES, SMALL_VM_MIPS, SMALL_VM_RAM));
//                vmList.add(createVm(i + 1, MEDIUM_VM_PES, MEDIUM_VM_MIPS, MEDIUM_VM_RAM));
//                vmList.add(createVm(i + 2, LARGE_VM_PES, LARGE_VM_MIPS/LARGE_VM_PES, LARGE_VM_RAM));
//            }
            for (int i=0;i<96;i++) {
            	vmList.add(createVm(i, SMALL_VM_PES, SMALL_VM_MIPS, SMALL_VM_RAM,SMALL_VM_BANDWIDTH));
            }
            for (int i=0;i<96;i++) {
            	vmList.add(createVm(96 + i + 1, MEDIUM_VM_PES, MEDIUM_VM_MIPS, MEDIUM_VM_RAM,MEDIUM_VM_BANDWIDTH));
            }
            for (int i=0;i<88;i++) {
            	vmList.add(createVm(96*2 + i + 2, LARGE_VM_PES, LARGE_VM_MIPS/LARGE_VM_PES, LARGE_VM_RAM,LARGE_VM_BANDWIDTH));
            }
            broker.submitGuestList(vmList);

            // Submit cloudlets
//            List<Cloudlet> cloudletList = createCloudlets(1000);
//            broker.submitCloudletList(cloudletList);

            CloudSim.startSimulation();

            // Calculate performance metrics
//            List<Cloudlet> finishedCloudlets = broker.getCloudletReceivedList();
//            printMetrics(finishedCloudlets);

            CloudSim.stopSimulation();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static Datacenter createDatacenter(String name) {
        List<Host> hostList = new ArrayList<>();
        for (int hostId = 0; hostId < NUM_HOSTS_PER_DC; hostId++) {
            List<Pe> peList = new ArrayList<>();
            for (int peId = 0; peId < HOST_PES; peId++) {
                peList.add(new Pe(peId, new PeProvisionerSimple(HOST_PE_MIPS)));
            }
            Host host = new Host(
                hid++,
                new RamProvisionerSimple(HOST_RAM),
                new BwProvisionerSimple(16000),
                HOST_STORAGE,
                peList,
                new VmSchedulerTimeShared(peList)
            );
            hostList.add(host);
        }
        DatacenterCharacteristics characteristics = new DatacenterCharacteristics(
            "x86", "Linux", "Xen", hostList, 10.0, 0.1, 0.1, 0.1, 0.1
        );

        try {
            return new Datacenter(name, characteristics, new VmAllocationWithSelectionPolicy(hostList, new SelectionPolicyFirstFit()), new ArrayList<>(), 0);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    private static Vm createVm(int id, int pes, int mips, int ram, int bw) {
        return new Vm(
            id, broker.getId(), mips, pes, ram, bw, 0, "Xen",
            new CloudletSchedulerTimeShared()
        );
    }

    private static List<Cloudlet> createCloudlets(int numCloudlets) {
        UtilizationModel utilizationModel = new UtilizationModelFull();
        List<Cloudlet> cloudletList = new ArrayList<>();
        for (int i = 0; i < numCloudlets; i++) {
            cloudletList.add(new Cloudlet(
                i, CLOUDLET_LENGTH, CLOUDLET_PES,
                CLOUDLET_FILESIZE, CLOUDLET_OUTPUTSIZE,
                utilizationModel, utilizationModel, utilizationModel
            ));
        }
        return cloudletList;
    }

    private static void printMetrics(List<Cloudlet> cloudlets) {
        double totalWaitTime = 0, totalResponseTime = 0;
        double makespan = 0, earliestStart = Double.MAX_VALUE, latestFinish = 0;
        
        for (Cloudlet c : cloudlets) {
            double wait = c.getExecStartTime() - c.getSubmissionTime();
            @SuppressWarnings("deprecation")
			double finish = c.getFinishTime();
            
            totalWaitTime += wait;
            totalResponseTime += (finish - c.getSubmissionTime());
            makespan = Math.max(makespan, finish);
            earliestStart = Math.min(earliestStart, c.getExecStartTime());
            latestFinish = Math.max(latestFinish, finish);
        }

        System.out.println("\n========= Performance Metrics =========");
        System.out.printf("Average Wait Time: %.2f sec\n", totalWaitTime / cloudlets.size());
        System.out.printf("Average Response Time: %.2f sec\n", totalResponseTime / cloudlets.size());
        System.out.printf("Makespan: %.2f sec\n", latestFinish - earliestStart);
        System.out.printf("Average Turnaround Time: %.2f sec\n", (totalResponseTime) / cloudlets.size());
    }
}
