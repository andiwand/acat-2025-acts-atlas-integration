rule all:
    input:
        "plots/clustering_pixel.pdf",
        "plots/clustering_strip.pdf",
        "plots/spot.pdf",
        "plots/tracking_efficiency_physics.pdf",
        "plots/tracking_efficiency_technical.pdf",
        "plots/tracking_resolution_d0.pdf",
        "plots/tracking_resolution_z0.pdf",
        "plots/tracking_resolution_ptqopt.pdf",

        "plots/monitoring/tracking_hits_pixel_inner.pdf",
        "plots/monitoring/tracking_hits_pixel.pdf",
        "plots/monitoring/tracking_hits_strip.pdf",

rule plot_clustering_pixel:
    input:
        script = "scripts/plot_clustering.py",
        root = "data/clustering/acts-expert-monitoring.root",
    output:
        "plots/clustering_pixel.pdf",
    shell:
        """
        python {input.script} {input.root} pixelalg --output {output}
        """

rule plot_clustering_strip:
    input:
        script = "scripts/plot_clustering.py",
        root = "data/clustering/acts-expert-monitoring.root",
    output:
        "plots/clustering_strip.pdf",
    shell:
        """
        python {input.script} {input.root} stripalg --output {output}
        """

rule plot_spot:
    input:
        script = "scripts/plot_spot.py",
        folder = "data/spot",
    output:
        "plots/spot.pdf",
    shell:
        """
        python {input.script} {input.folder} --output {output}
        """

rule plot_tracking_efficiency:
    input:
        script = "scripts/plot_tracking_efficiency.py",
        root_athena_default = "data/tracking/IDTPM.C000.ttbar_pu200_EFsel.HIST.root",
        root_acts_fast = "data/tracking/IDTPM_TTBAR_Acts_C100_digital_Main30July2025.root",
        root_acts_slow = "data/tracking/IDTPM_TTBAR_Acts_C100DEFAULT_digital.root",
        root_acts_slow_analog = "data/tracking/IDTPM_TTBAR_Acts_C100DEFAULT_analog.root",
    output:
        "plots/tracking_efficiency_{mode}.pdf",
    shell:
        """
        python {input.script} {input.root_athena_default} {wildcards.mode} \
        --input-acts-fast {input.root_acts_fast} \
        --input-acts-slow {input.root_acts_slow} \
        --output {output}
        """

rule plot_tracking_resolution:
    input:
        script = "scripts/plot_tracking_resolution.py",
        root_athena_default = "data/tracking/IDTPM.C000.ttbar_pu200_EFsel.HIST.root",
        root_acts_fast = "data/tracking/IDTPM_TTBAR_Acts_C100_digital_Main30July2025.root",
        root_acts_slow = "data/tracking/IDTPM_TTBAR_Acts_C100DEFAULT_digital.root",
        root_acts_slow_analog = "data/tracking/IDTPM_TTBAR_Acts_C100DEFAULT_analog.root",
    output:
        "plots/tracking_resolution_{mode}.pdf",
    shell:
        """
        python {input.script} {input.root_athena_default} {wildcards.mode} \
        --input-acts-fast {input.root_acts_fast} \
        --input-acts-slow {input.root_acts_slow} \
        --output {output}
        """

rule plot_tracking_hits:
    input:
        script = "scripts/plot_tracking_hits.py",
        root_athena_default = "data/tracking/IDTPM.C000.ttbar_pu200_EFsel.HIST.root",
        root_acts_fast = "data/tracking/IDTPM_TTBAR_Acts_C100_digital_Main30July2025.root",
        root_acts_slow = "data/tracking/IDTPM_TTBAR_Acts_C100DEFAULT_digital.root",
        root_acts_slow_analog = "data/tracking/IDTPM_TTBAR_Acts_C100DEFAULT_analog.root",
    output:
        "plots/monitoring/tracking_hits_{mode}.pdf",
    shell:
        """
        python {input.script} {input.root_athena_default} {wildcards.mode} \
        --input-acts-fast {input.root_acts_fast} \
        --input-acts-slow {input.root_acts_slow} \
        --output {output}
        """
