"""
Reusable visualization utilities for the IPL Analytics Platform.

This module provides generic plotting functions built on top of
Matplotlib and Seaborn.

The functions operate on analytical DataFrames and are intentionally
domain-agnostic so they can be reused across exploratory analysis,
report generation, and model evaluation.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "plot_bar",
    "plot_horizontal_bar",
    "plot_line",
    "plot_pie",
    "plot_histogram",
    "plot_box",
    "plot_heatmap",
    "save_figure",
    "close_all_figures",
]

def _apply_plot_style(
    figsize: tuple[int, int] = (12, 6),
) -> None:
    """
    Apply consistent plotting style.

    Parameters
    ----------
    figsize : tuple[int, int], default=(12, 6)
        Figure size in inches.
    """
    plt.figure(figsize=figsize)

    plt.grid(
        alpha=0.3,
        linestyle="--",
    )

def plot_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
    rotation: int = 45,
) -> plt.Axes:
    """
    Create a bar chart.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        Column used for x-axis.
    y_col : str
        Column used for y-axis.
    title : str
        Plot title.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    rotation : int, default=45
        Rotation angle for x-axis labels.

    Returns
    -------
    matplotlib.axes.Axes
        Generated plot axes.
    """
    _apply_plot_style()

    ax = plt.gca()

    ax.bar(
        df[x_col],
        df[y_col],
    )

    ax.set_title(title)

    ax.set_xlabel(xlabel)

    ax.set_ylabel(ylabel)

    plt.xticks(rotation=rotation)

    plt.tight_layout()

    return ax

def plot_horizontal_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
) -> plt.Axes:
    """
    Create a horizontal bar chart.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        Column used for x-axis.
    y_col : str
        Column used for y-axis.
    title : str
        Plot title.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.

    Returns
    -------
    matplotlib.axes.Axes
        Generated plot axes.
    """
    _apply_plot_style()

    ax = plt.gca()

    ax.barh(
        df[x_col],
        df[y_col],
    )

    ax.set_title(title)

    ax.set_xlabel(xlabel)

    ax.set_ylabel(ylabel)

    plt.tight_layout()

    return ax

def plot_line(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str,
    ylabel: str,
    rotation: int = 45,
) -> plt.Axes:
    """
    Create a line plot.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    x_col : str
        Column used for x-axis.
    y_col : str
        Column used for y-axis.
    title : str
        Plot title.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    rotation : int, default=45
        Rotation angle for x-axis labels.

    Returns
    -------
    matplotlib.axes.Axes
        Generated plot axes.
    """
    _apply_plot_style()

    ax = plt.gca()

    ax.plot(
        df[x_col],
        df[y_col],
        marker="o",
    )

    ax.set_title(title)

    ax.set_xlabel(xlabel)

    ax.set_ylabel(ylabel)

    plt.xticks(rotation=rotation)

    plt.tight_layout()

    return ax

def plot_pie(
    df: pd.DataFrame,
    value_col: str,
    label_col: str,
    title: str,
) -> plt.Axes:
    """
    Create a pie chart.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    value_col : str
        Column used for values.
    label_col : str
        Column used for labels.
    title : str
        Plot title.

    Returns
    -------
    matplotlib.axes.Axes
        Generated plot axes.
    """
    _apply_plot_style()

    ax = plt.gca()

    ax.pie(
        df[value_col],
        labels=df[label_col],
        autopct="%1.1f%%",
    )

    ax.set_title(title)

    plt.tight_layout()

    return ax

def plot_histogram(
    df: pd.DataFrame,
    column: str,
    title: str,
    xlabel: str,
    ylabel: str,
    bins: int = 10,
) -> plt.Axes:
    """
    Create a histogram.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    column : str
        Column used for histogram.
    title : str
        Plot title.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.
    bins : int, default=10
        Number of bins.

    Returns
    -------
    matplotlib.axes.Axes
        Generated plot axes.
    """
    _apply_plot_style()

    ax = plt.gca()

    ax.hist(
        df[column],
        bins=bins,
    )

    ax.set_title(title)

    ax.set_xlabel(xlabel)

    ax.set_ylabel(ylabel)

    plt.tight_layout()

    return ax

def plot_box(
    df: pd.DataFrame,
    column: str,
    title: str,
    ylabel: str,
) -> plt.Axes:
    """
    Create a box plot.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    column : str
        Column used for box plot.
    title : str
        Plot title.
    ylabel : str
        Y-axis label.

    Returns
    -------
    matplotlib.axes.Axes
        Generated plot axes.
    """
    _apply_plot_style()

    ax = plt.gca()

    ax.boxplot(
        df[column],
    )

    ax.set_title(title)

    ax.set_ylabel(ylabel)

    plt.tight_layout()

    return ax

def plot_heatmap(
    data: pd.DataFrame,
    title: str,
    xlabel: str,
    ylabel: str,
) -> plt.Axes:
    """
    Plot a heatmap from a pivoted dataframe.

    Parameters
    ----------
    data : pd.DataFrame
        Pivoted dataframe with numeric values.
    title : str
        Plot title.
    xlabel : str
        X-axis label.
    ylabel : str
        Y-axis label.

    Returns
    -------
    matplotlib.axes.Axes
        Generated plot axes.
    """
    _apply_plot_style()

    ax = plt.gca()

    image = ax.imshow(
        data.values,
        aspect="auto",
        interpolation="nearest",
    )

    ax.set_xticks(range(len(data.columns)))
    ax.set_xticklabels(data.columns, rotation=90)

    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(data.index)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    plt.colorbar(image, ax=ax)
    plt.tight_layout()

    return ax

def save_figure(
    filepath: str | Path,
    dpi: int = 300,
) -> None:
    """
    Save the current figure.

    Parameters
    ----------
    filepath : str | Path
        Output file path.
    dpi : int, default=300
        Resolution of the saved figure.
    """
    plt.savefig(
        filepath,
        dpi=dpi,
        bbox_inches="tight",
    )

    logger.info(
        "Figure saved to %s",
        filepath,
    )

def close_all_figures() -> None:
    """
    Close all open Matplotlib figures.
    """
    plt.close("all")