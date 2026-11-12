from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Cell, ConsolidatedCellReport


@login_required
def print_cell_reports(request, pk):
    cell = get_object_or_404(Cell, pk=pk)
    reports = cell.reports.select_related('facilitated_by', 'submitted_by').all()
    return render(request, 'print/cell_reports.html', {'cell': cell, 'reports': reports})


@login_required
def print_consolidated_report(request, pk):
    report = get_object_or_404(ConsolidatedCellReport, pk=pk)
    return render(request, 'print/consolidated_report.html', {'report': report})
