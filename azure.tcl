namespace eval ttk::theme::azure {
    variable colors
    array set colors {
        -fg             "#000000"
        -bg             "#ffffff"
        -disabledfg     "#737373"
        -disabledbg     "#ffffff"
        -selectfg       "#ffffff"
        -selectbg       "#007fff"
    }

    ttk::style theme create azure -parent default -settings {
        ttk::style configure "." \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor $colors(-selectbg) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -insertcolor $colors(-fg) \
            -insertwidth 1 \
            -fieldbackground $colors(-bg) \
            -font {"Segoe UI" 10} \
            -borderwidth 1 \
            -relief flat

        ttk::style map "." \
            -background [list disabled $colors(-disabledbg) \
                            active $colors(-selectbg)] \
            -foreground [list disabled $colors(-disabledfg)] \
            -selectbackground [list !focus $colors(-selectbg)] \
            -selectforeground [list !focus white]

        # Frame principal
        ttk::style configure Main.TFrame \
            -background "#ffffff"

        # Cards
        ttk::style configure Card.TFrame \
            -background "#ffffff" \
            -relief solid \
            -borderwidth 1 \
            -bordercolor "#e0e0e0"

        ttk::style configure CardHover.TFrame \
            -background "#f8f9fa" \
            -relief solid \
            -borderwidth 1 \
            -bordercolor "#1a73e8"

        # Metric Cards
        ttk::style configure Metric.TFrame \
            -background "#ffffff" \
            -relief solid \
            -borderwidth 1 \
            -bordercolor "#e0e0e0"

        ttk::style configure MetricHover.TFrame \
            -background "#f8f9fa" \
            -relief solid \
            -borderwidth 1 \
            -bordercolor "#1a73e8"

        # Button
        ttk::style configure TButton \
            -padding {5 2} \
            -width -10 \
            -anchor center

        ttk::style map TButton \
            -background [list pressed "#1557b0" \
                            active "#1a73e8"] \
            -relief [list pressed sunken] \
            -padding [list pressed {5 2}]

        # Entry
        ttk::style configure TEntry \
            -padding 3 \
            -insertwidth 1 \
            -fieldbackground white \
            -borderwidth 1 \
            -relief solid

        # Combobox
        ttk::style configure TCombobox \
            -padding 3 \
            -fieldbackground white

        # Notebook
        ttk::style configure TNotebook \
            -padding 2 \
            -background "#ffffff"

        ttk::style configure TNotebook.Tab \
            -padding {12 4} \
            -font {"Segoe UI" 10}

        ttk::style map TNotebook.Tab \
            -background [list selected "#ffffff" \
                            active "#f0f0f0" \
                            !active "#f8f9fa"] \
            -foreground [list selected "#1a73e8" \
                            active "#202124" \
                            !active "#5f6368"] \
            -expand [list selected {2 2 2 0}]

        # Treeview
        ttk::style configure Treeview \
            -background white \
            -foreground black \
            -fieldbackground white \
            -font {"Segoe UI" 10} \
            -relief solid \
            -borderwidth 1

        ttk::style configure Treeview.Heading \
            -font {"Segoe UI" 10 bold} \
            -background "#f8f9fa" \
            -foreground "#202124" \
            -relief raised \
            -borderwidth 1

        ttk::style map Treeview \
            -background [list selected "#e8f0fe"] \
            -foreground [list selected "#1a73e8"]

        # Scrollbar
        ttk::style configure TScrollbar \
            -background "#ffffff" \
            -troughcolor "#f8f9fa" \
            -bordercolor "#e0e0e0" \
            -arrowcolor "#5f6368" \
            -relief solid \
            -borderwidth 1

        ttk::style map TScrollbar \
            -background [list pressed "#1557b0" \
                            active "#1a73e8"] \
            -troughcolor [list pressed "#f0f0f0" \
                             active "#f8f9fa"]
    }
} 