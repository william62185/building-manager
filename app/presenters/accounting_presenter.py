"""
Presenter del módulo de contabilidad (MVP).
Consolida movimientos de pagos, gastos y asientos contables,
calcula totales y gestiona exportaciones.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any

from manager.app.logger import logger
from manager.app.paths_config import EXPORTS_DIR, ensure_dirs


class AccountingPresenter:
    """Lógica de presentación para el módulo de contabilidad."""

    def __init__(
        self,
        on_back: Optional[Callable[[], None]] = None,
        on_navigate_to_dashboard: Optional[Callable[[], None]] = None,
    ):
        self._on_back = on_back
        self._on_navigate_to_dashboard = on_navigate_to_dashboard

        from manager.app.services.payment_service import payment_service
        from manager.app.services.expense_service import expense_service
        from manager.app.services.accounting_service import accounting_service

        self._payment_service = payment_service
        self._expense_service = expense_service
        self._accounting_service = accounting_service

    # ------------------------------------------------------------------
    # Consolidación y normalización
    # ------------------------------------------------------------------

    def consolidate_movements(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        movement_type: Optional[str] = None,
        tenant_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Consolida y normaliza movimientos de pagos, gastos y asientos contables.

        Args:
            date_from: Fecha inicio en formato YYYY-MM-DD (inclusive).
            date_to: Fecha fin en formato YYYY-MM-DD (inclusive).
            movement_type: "ingreso" | "egreso" | "ajuste" | None (todos).
            tenant_id: Filtrar por ID de inquilino (aplica a pagos y asientos manuales).

        Returns:
            Lista de movimientos normalizados ordenados por fecha DESC.
        """
        movements: List[Dict[str, Any]] = []

        # --- Pagos ---
        try:
            self._payment_service._load_data()
            for pago in self._payment_service.get_all_payments():
                mov = self._normalize_payment(pago)
                if mov:
                    movements.append(mov)
        except Exception as exc:
            logger.warning("Error al cargar pagos para consolidación: %s", exc)

        # --- Gastos ---
        try:
            self._expense_service._load_data()
            for gasto in self._expense_service.get_all_expenses():
                mov = self._normalize_expense(gasto)
                if mov:
                    movements.append(mov)
        except Exception as exc:
            logger.warning("Error al cargar gastos para consolidación: %s", exc)

        # --- Asientos contables ---
        try:
            self._accounting_service._load_data()
            for asiento in self._accounting_service.get_all_entries():
                movs = self._normalize_entry(asiento)
                movements.extend(movs)
        except Exception as exc:
            logger.warning("Error al cargar asientos contables para consolidación: %s", exc)

        # --- Aplicar filtros en memoria ---
        filtered = self._apply_filters(movements, date_from, date_to, movement_type, tenant_id)

        # --- Ordenar por fecha DESC ---
        filtered.sort(key=lambda m: m["fecha"], reverse=True)
        return filtered

    def _normalize_payment(self, pago: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normaliza un pago al formato unificado de movimiento."""
        try:
            fecha_raw = pago.get("fecha_pago", "")
            # fecha_pago viene en DD/MM/YYYY
            dt = datetime.strptime(fecha_raw, "%d/%m/%Y")
            fecha = dt.strftime("%Y-%m-%d")
            fecha_display = fecha_raw  # ya está en DD/MM/YYYY
            nombre = pago.get("nombre_inquilino", "")
            return {
                "fecha": fecha,
                "fecha_display": fecha_display,
                "tipo": "ingreso",
                "descripcion": f"Pago arriendo - {nombre}",
                "referencia": nombre,
                "monto": float(pago.get("monto", 0)),
                "direccion": "entrada",
                "fuente": "pago",
                "id_original": pago.get("id"),
                "id_inquilino": pago.get("id_inquilino"),
            }
        except Exception as exc:
            logger.warning("Error al normalizar pago id=%s: %s", pago.get("id"), exc)
            return None

    def _normalize_expense(self, gasto: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normaliza un gasto al formato unificado de movimiento."""
        try:
            fecha = gasto.get("fecha", "")  # ya en YYYY-MM-DD
            dt = datetime.strptime(fecha, "%Y-%m-%d")
            fecha_display = dt.strftime("%d/%m/%Y")
            categoria = gasto.get("categoria", "")
            subtipo = gasto.get("subtipo", "")
            descripcion = f"{categoria} - {subtipo}" if subtipo else categoria
            return {
                "fecha": fecha,
                "fecha_display": fecha_display,
                "tipo": "egreso",
                "descripcion": descripcion,
                "referencia": categoria,
                "monto": float(gasto.get("monto", 0)),
                "direccion": "salida",
                "fuente": "gasto",
                "id_original": gasto.get("id"),
                "id_inquilino": None,
            }
        except Exception as exc:
            logger.warning("Error al normalizar gasto id=%s: %s", gasto.get("id"), exc)
            return None

    def _normalize_entry(self, asiento: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Normaliza un asiento contable al formato unificado.
        Un asiento de apertura puede generar uno o dos movimientos.
        """
        tipo = asiento.get("tipo", "manual")
        fecha = asiento.get("fecha", "")
        try:
            dt = datetime.strptime(fecha, "%Y-%m-%d")
            fecha_display = dt.strftime("%d/%m/%Y")
        except Exception:
            fecha_display = fecha

        if tipo == "apertura":
            return self._normalize_opening_entry(asiento, fecha, fecha_display)
        else:
            return self._normalize_manual_entry(asiento, fecha, fecha_display)

    def _normalize_opening_entry(
        self, asiento: Dict[str, Any], fecha: str, fecha_display: str
    ) -> List[Dict[str, Any]]:
        """Normaliza un asiento de apertura (puede generar 1 o 2 movimientos)."""
        monto_ingresos = float(asiento.get("monto_ingresos", 0) or 0)
        monto_egresos = float(asiento.get("monto_egresos", 0) or 0)
        descripcion = asiento.get("descripcion", "Saldo inicial")
        entry_id = asiento.get("id")
        movimientos = []

        if monto_ingresos > 0:
            movimientos.append({
                "fecha": fecha,
                "fecha_display": fecha_display,
                "tipo": "ajuste",
                "descripcion": descripcion,
                "referencia": "Saldo inicial",
                "monto": monto_ingresos,
                "direccion": "entrada",
                "fuente": "apertura",
                "id_original": entry_id,
                "id_inquilino": None,
            })

        if monto_egresos > 0:
            movimientos.append({
                "fecha": fecha,
                "fecha_display": fecha_display,
                "tipo": "ajuste",
                "descripcion": descripcion,
                "referencia": "Saldo inicial",
                "monto": monto_egresos,
                "direccion": "salida",
                "fuente": "apertura",
                "id_original": entry_id,
                "id_inquilino": None,
            })

        return movimientos

    def _normalize_manual_entry(
        self, asiento: Dict[str, Any], fecha: str, fecha_display: str
    ) -> List[Dict[str, Any]]:
        """Normaliza un asiento manual."""
        nombre_inquilino = asiento.get("nombre_inquilino", "")
        tipo_ajuste = asiento.get("tipo_ajuste", "")
        referencia = nombre_inquilino if nombre_inquilino else tipo_ajuste
        return [{
            "fecha": fecha,
            "fecha_display": fecha_display,
            "tipo": "ajuste",
            "descripcion": asiento.get("descripcion", ""),
            "referencia": referencia,
            "monto": float(asiento.get("monto", 0)),
            "direccion": asiento.get("direccion", "entrada"),
            "fuente": "manual",
            "id_original": asiento.get("id"),
            "id_inquilino": asiento.get("id_inquilino"),
        }]

    def _apply_filters(
        self,
        movements: List[Dict[str, Any]],
        date_from: Optional[str],
        date_to: Optional[str],
        movement_type: Optional[str],
        tenant_id: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Aplica filtros en memoria sin modificar la lista original."""
        result = movements

        if date_from:
            result = [m for m in result if m["fecha"] >= date_from]

        if date_to:
            result = [m for m in result if m["fecha"] <= date_to]

        if movement_type:
            result = [m for m in result if m["tipo"] == movement_type]

        if tenant_id is not None:
            result = [
                m for m in result
                if m.get("id_inquilino") == tenant_id
            ]

        return result

    # ------------------------------------------------------------------
    # Cálculo de totales
    # ------------------------------------------------------------------

    def calculate_totals(self, movements: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calcula totales de ingresos, egresos y balance neto.

        Args:
            movements: Lista de movimientos normalizados.

        Returns:
            Dict con total_ingresos, total_egresos y balance_neto.
        """
        total_ingresos = sum(
            m["monto"] for m in movements if m.get("direccion") == "entrada"
        )
        total_egresos = sum(
            m["monto"] for m in movements if m.get("direccion") == "salida"
        )
        balance_neto = total_ingresos - total_egresos
        return {
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
            "balance_neto": balance_neto,
        }

    # ------------------------------------------------------------------
    # Estado de resultados
    # ------------------------------------------------------------------

    def get_income_statement(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """
        Genera el estado de resultados para un período dado.

        Args:
            date_from: Fecha inicio en formato YYYY-MM-DD.
            date_to: Fecha fin en formato YYYY-MM-DD.

        Returns:
            Dict con ingresos_arriendo, egresos_por_categoria, ajustes_netos,
            balance_neto, date_from y date_to.
        """
        movements = self.consolidate_movements(date_from=date_from, date_to=date_to)

        ingresos_arriendo = sum(
            m["monto"] for m in movements
            if m["fuente"] == "pago" and m["direccion"] == "entrada"
        )

        egresos_por_categoria: Dict[str, float] = {}
        for m in movements:
            if m["fuente"] == "gasto":
                cat = m["referencia"] or "Sin categoría"
                egresos_por_categoria[cat] = egresos_por_categoria.get(cat, 0.0) + m["monto"]

        ajustes_entradas = sum(
            m["monto"] for m in movements
            if m["fuente"] in ("manual", "apertura") and m["direccion"] == "entrada"
        )
        ajustes_salidas = sum(
            m["monto"] for m in movements
            if m["fuente"] in ("manual", "apertura") and m["direccion"] == "salida"
        )
        ajustes_netos = ajustes_entradas - ajustes_salidas

        balance_neto = ingresos_arriendo - sum(egresos_por_categoria.values()) + ajustes_netos

        return {
            "date_from": date_from,
            "date_to": date_to,
            "ingresos_arriendo": ingresos_arriendo,
            "egresos_por_categoria": egresos_por_categoria,
            "ajustes_netos": ajustes_netos,
            "balance_neto": balance_neto,
        }

    # ------------------------------------------------------------------
    # Exportación
    # ------------------------------------------------------------------

    def export_ledger(
        self,
        movements: List[Dict[str, Any]],
        fmt: str,
        period_label: str,
    ) -> Path:
        """
        Exporta el libro de movimientos a CSV o TXT.

        Args:
            movements: Lista de movimientos normalizados.
            fmt: "csv" o "txt".
            period_label: Etiqueta del período (ej. "2024-03").

        Returns:
            Path del archivo generado.
        """
        ensure_dirs()
        filename = f"libro_movimientos_{period_label}.{fmt}"
        output_path = EXPORTS_DIR / filename

        if fmt == "csv":
            self._export_ledger_csv(movements, output_path)
        else:
            self._export_ledger_txt(movements, output_path)

        logger.info("Libro de movimientos exportado: %s", output_path)
        return output_path

    def _export_ledger_csv(self, movements: List[Dict[str, Any]], path: Path) -> None:
        """Escribe el libro de movimientos en formato CSV."""
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "Tipo", "Descripción", "Referencia", "Monto", "Dirección"])
            for m in movements:
                writer.writerow([
                    m.get("fecha_display", m.get("fecha", "")),
                    m.get("tipo", ""),
                    m.get("descripcion", ""),
                    m.get("referencia", ""),
                    m.get("monto", 0),
                    m.get("direccion", ""),
                ])

    def _export_ledger_txt(self, movements: List[Dict[str, Any]], path: Path) -> None:
        """Escribe el libro de movimientos en formato tabular TXT."""
        col_widths = [12, 10, 40, 30, 15, 10]
        headers = ["Fecha", "Tipo", "Descripción", "Referencia", "Monto", "Dirección"]
        sep = "-" * (sum(col_widths) + len(col_widths) * 3 + 1)

        def row_str(values: List[str]) -> str:
            return "| " + " | ".join(
                str(v).ljust(w) for v, w in zip(values, col_widths)
            ) + " |"

        with open(path, "w", encoding="utf-8-sig") as f:
            f.write("LIBRO DE MOVIMIENTOS\n")
            f.write(sep + "\n")
            f.write(row_str(headers) + "\n")
            f.write(sep + "\n")
            for m in movements:
                f.write(row_str([
                    m.get("fecha_display", m.get("fecha", "")),
                    m.get("tipo", ""),
                    m.get("descripcion", ""),
                    m.get("referencia", ""),
                    f"{m.get('monto', 0):,.2f}",
                    m.get("direccion", ""),
                ]) + "\n")
            f.write(sep + "\n")

    def export_income_statement(
        self,
        data: Dict[str, Any],
        fmt: str,
        period_label: str,
    ) -> Path:
        """
        Exporta el estado de resultados a CSV o TXT.

        Args:
            data: Dict retornado por get_income_statement.
            fmt: "csv" o "txt".
            period_label: Etiqueta del período (ej. "2024-03").

        Returns:
            Path del archivo generado.
        """
        ensure_dirs()
        filename = f"estado_resultados_{period_label}.{fmt}"
        output_path = EXPORTS_DIR / filename

        if fmt == "csv":
            self._export_income_statement_csv(data, output_path)
        else:
            self._export_income_statement_txt(data, output_path)

        logger.info("Estado de resultados exportado: %s", output_path)
        return output_path

    def _export_income_statement_csv(self, data: Dict[str, Any], path: Path) -> None:
        """Escribe el estado de resultados en formato CSV."""
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Estado de Resultados"])
            writer.writerow(["Período", f"{data.get('date_from')} — {data.get('date_to')}"])
            writer.writerow([])
            writer.writerow(["INGRESOS"])
            writer.writerow(["Concepto", "Monto"])
            writer.writerow(["Ingresos por arriendo", data.get("ingresos_arriendo", 0)])
            writer.writerow([])
            writer.writerow(["EGRESOS POR CATEGORÍA"])
            writer.writerow(["Categoría", "Monto"])
            for cat, monto in data.get("egresos_por_categoria", {}).items():
                writer.writerow([cat, monto])
            writer.writerow([])
            writer.writerow(["AJUSTES"])
            writer.writerow(["Ajustes netos", data.get("ajustes_netos", 0)])
            writer.writerow([])
            writer.writerow(["BALANCE NETO", data.get("balance_neto", 0)])

    def _export_income_statement_txt(self, data: Dict[str, Any], path: Path) -> None:
        """Escribe el estado de resultados en formato TXT legible."""
        sep = "=" * 60
        sep_thin = "-" * 60

        with open(path, "w", encoding="utf-8-sig") as f:
            f.write(sep + "\n")
            f.write("  ESTADO DE RESULTADOS\n")
            f.write(f"  Período: {data.get('date_from')} — {data.get('date_to')}\n")
            f.write(sep + "\n\n")

            f.write("INGRESOS\n")
            f.write(sep_thin + "\n")
            f.write(f"  Ingresos por arriendo:  {data.get('ingresos_arriendo', 0):>15,.2f}\n\n")

            f.write("EGRESOS POR CATEGORÍA\n")
            f.write(sep_thin + "\n")
            for cat, monto in data.get("egresos_por_categoria", {}).items():
                f.write(f"  {cat:<35} {monto:>15,.2f}\n")
            total_egresos = sum(data.get("egresos_por_categoria", {}).values())
            f.write(f"  {'Total egresos':<35} {total_egresos:>15,.2f}\n\n")

            f.write("AJUSTES\n")
            f.write(sep_thin + "\n")
            f.write(f"  Ajustes netos:          {data.get('ajustes_netos', 0):>15,.2f}\n\n")

            f.write(sep + "\n")
            f.write(f"  BALANCE NETO:           {data.get('balance_neto', 0):>15,.2f}\n")
            f.write(sep + "\n")

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def go_back(self) -> None:
        """Navega a la pantalla anterior."""
        if self._on_back:
            self._on_back()

    def go_to_dashboard(self) -> None:
        """Navega al dashboard."""
        if self._on_navigate_to_dashboard:
            self._on_navigate_to_dashboard()
