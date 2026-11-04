#!/usr/bin/env python3
"""
Plot the band structure computed by the Q3 band-structure example.

Reads the ESSE `eigenvalues_at_kpoints` record from the band run's results, places the
k-points along the path by their Cartesian distance (crystal coordinates converted with the
reciprocal lattice of the cell in `structure.material`), and shifts the energies so that the
Fermi energy of the SCF run is at zero. The SCF Fermi energy is used because the band run
samples a path, not the Brillouin zone. Requires matplotlib.

Usage:
    python3 plot_bandstructure.py
    python3 plot_bandstructure.py outdir/si_results.json --scf-results outdir/si_scf_results.json \
        --labels G X W K G L --output bandstructure.png
"""

import argparse
import json
import logging
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as pyplot  # noqa: E402 -- the backend is selected above

LOGGER = logging.getLogger("plot_bandstructure")

ELECTRONVOLTS_PER_UNIT = {"eV": 1.0, "Ry": 13.605693122994, "hartree": 27.211386245988}
DISPLAY_LABELS = {"G": "Γ", "Gamma": "Γ"}
PARALLEL_TOLERANCE = 1.0e-6


def parse_arguments():
    parser = argparse.ArgumentParser(description="Plot a Q3 band structure.")
    parser.add_argument("results_path", nargs="?", default="outdir/si_results.json")
    parser.add_argument("--scf-results", default="outdir/si_scf_results.json")
    parser.add_argument("--labels", nargs="+", default=["G", "X", "W", "K", "G", "L"])
    parser.add_argument("--output", default="bandstructure.png")
    parser.add_argument("--energy-window", nargs=2, type=float, default=[-13.0, 8.0])
    parser.add_argument("--log-level", default="error",
                        choices=["critical", "error", "warning", "info", "debug"])
    return parser.parse_args()


def read_record(results, record_name):
    for record in results["properties"]["records"]:
        if record["name"] == record_name:
            return record
    raise KeyError(f"no '{record_name}' record in the results")


def to_electronvolts(value, units):
    return value * ELECTRONVOLTS_PER_UNIT[units]


def read_fermi_energy(scf_results_path):
    """SCF Fermi energy in eV, or 0.0 when the SCF results are not available."""
    if not Path(scf_results_path).is_file():
        LOGGER.warning("%s not found: energies are not shifted to the Fermi energy", scf_results_path)
        return 0.0
    record = read_record(json.loads(Path(scf_results_path).read_text()), "fermi_energy")
    return to_electronvolts(record["value"], record["units"])


def cross_product(first, second):
    return [
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    ]


def dot_product(first, second):
    return sum(first_component * second_component for first_component, second_component in zip(first, second))


def reciprocal_lattice_vectors(results):
    """Reciprocal lattice vectors in inverse angstrom, 2 pi included."""
    vectors = results["structure"]["material"]["lattice"]["vectors"]
    lattice_vectors = [vectors["a"], vectors["b"], vectors["c"]]
    cell_volume = dot_product(lattice_vectors[0], cross_product(lattice_vectors[1], lattice_vectors[2]))
    reciprocal_vectors = []
    for index in range(3):
        cross = cross_product(lattice_vectors[(index + 1) % 3], lattice_vectors[(index + 2) % 3])
        reciprocal_vectors.append([2.0 * math.pi * component / cell_volume for component in cross])
    return reciprocal_vectors


def crystal_to_cartesian(kpoint, reciprocal_vectors):
    return [sum(kpoint[index] * reciprocal_vectors[index][axis] for index in range(3)) for axis in range(3)]


def path_distances(kpoints_crystal, reciprocal_vectors):
    kpoints_cartesian = [crystal_to_cartesian(kpoint, reciprocal_vectors) for kpoint in kpoints_crystal]
    distances = [0.0]
    for previous, current in zip(kpoints_cartesian, kpoints_cartesian[1:]):
        distances.append(distances[-1] + math.dist(previous, current))
    return distances


def is_direction_change(previous, current, following):
    incoming = [current[axis] - previous[axis] for axis in range(3)]
    outgoing = [following[axis] - current[axis] for axis in range(3)]
    return math.hypot(*cross_product(incoming, outgoing)) > PARALLEL_TOLERANCE


def vertex_indices(kpoints_crystal):
    """Indices of the path ends and of the k-points where the path changes direction."""
    indices = [0]
    for index in range(1, len(kpoints_crystal) - 1):
        if is_direction_change(kpoints_crystal[index - 1], kpoints_crystal[index], kpoints_crystal[index + 1]):
            indices.append(index)
    indices.append(len(kpoints_crystal) - 1)
    return indices


def bands_by_spin(record, fermi_energy):
    """{spin: (kpoints, [band][kpoint] energies in eV relative to the Fermi energy)}."""
    channels = {}
    for entry in record["values"]:
        for channel in entry["eigenvalues"]:
            kpoints, energies_per_kpoint = channels.setdefault(channel["spin"], ([], []))
            kpoints.append(entry["kpoint"])
            energies_per_kpoint.append(
                [to_electronvolts(energy, record["units"]) - fermi_energy for energy in channel["energies"]]
            )
    return {spin: (kpoints, [list(band) for band in zip(*energies)]) for spin, (kpoints, energies) in channels.items()}


def tick_labels(labels, number_of_vertices):
    if len(labels) != number_of_vertices:
        LOGGER.warning("%d labels for %d path vertices: ticks are left unlabeled", len(labels), number_of_vertices)
        return [""] * number_of_vertices
    return [DISPLAY_LABELS.get(label, label) for label in labels]


def draw_bands(axes, distances, bands, color):
    for band in bands:
        axes.plot(distances, band, color=color, linewidth=1.0)


def style_axes(axes, tick_positions, labels, energy_window):
    for position in tick_positions:
        axes.axvline(position, color="grey", linewidth=0.5)
    axes.axhline(0.0, color="grey", linewidth=0.5, linestyle="--")
    axes.set_xticks(tick_positions)
    axes.set_xticklabels(labels)
    axes.set_xlim(tick_positions[0], tick_positions[-1])
    axes.set_ylim(*energy_window)
    axes.set_ylabel("E - E$_F$ (eV)")


def plot(channels, reciprocal_vectors, arguments):
    figure, axes = pyplot.subplots(figsize=(6, 5))
    colors = ["tab:blue", "tab:red"]
    for color, (kpoints, bands) in zip(colors, channels.values()):
        distances = path_distances(kpoints, reciprocal_vectors)
        draw_bands(axes, distances, bands, color)
    vertices = vertex_indices(kpoints)
    style_axes(axes, [distances[index] for index in vertices], tick_labels(arguments.labels, len(vertices)),
               arguments.energy_window)
    figure.tight_layout()
    figure.savefig(arguments.output, dpi=200)
    LOGGER.info("band structure written to %s", arguments.output)


def main():
    arguments = parse_arguments()
    logging.basicConfig(level=arguments.log_level.upper(), format="%(levelname)s: %(message)s")
    results = json.loads(Path(arguments.results_path).read_text())
    fermi_energy = read_fermi_energy(arguments.scf_results)
    channels = bands_by_spin(read_record(results, "eigenvalues_at_kpoints"), fermi_energy)
    plot(channels, reciprocal_lattice_vectors(results), arguments)


if __name__ == "__main__":
    main()
