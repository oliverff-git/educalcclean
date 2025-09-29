# Streamlit Development Rules & Best Practices

## ⚠️ CRITICAL: What Breaks Streamlit

### 1. CSS That Breaks Material Icons
**NEVER USE:**
- `:contains()` pseudo-selector (not real CSS, breaks everything)
- CSS that targets Material Icon spans or tries to replace them
- `font-size: 0` to hide text (breaks icon rendering)
- Replacing arrow content with `::before` or `::after` pseudo-elements

**WHAT HAPPENS:**
- Material icons show as text like "keyboard_arrow_right" or "keyboard_double_arrow_right"
- Expandable sections break
- Navigation elements fail

### 2. Mixing `unsafe_allow_html=True` with Material Icons
```python
# ❌ BAD - Icons won't render
st.markdown(":material/info:", unsafe_allow_html=True)

# ✅ GOOD - Icons render properly
st.markdown(":material/info:")
```

## ✅ Safe Styling Approaches

### 1. Use config.toml ONLY for Colors
```toml
[theme]
primaryColor = "#374151"        # Safe
backgroundColor = "#FFFFFF"      # Safe
secondaryBackgroundColor = "#F9FAFB"  # Safe
textColor = "#111827"           # Safe
font = "sans serif"             # Safe
```

### 2. Use Streamlit's Native Components for Layout
```python
# Professional boxing without CSS
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Label", "Value")

# Clean info boxes
st.info("**Bold text** for emphasis")

# Headers with markdown
st.markdown("### Section Title")
st.markdown("**Important:** Bold text only")
```

### 3. Limited Safe CSS Properties
If you MUST use CSS, only use:
- Simple color changes (but prefer config.toml)
- Padding/margin adjustments (minimal)
- Border colors (not structure)
- NEVER touch font-size globally
- NEVER interfere with Streamlit's icon system

## 📋 Streamlit Design Limitations

1. **Limited Customization**: Streamlit is opinionated by design
2. **Component Isolation**: Can't target specific components reliably
3. **Class Names Change**: Internal classes may change between versions
4. **No Component IDs**: Can't assign unique IDs to most components
5. **Global CSS Effects**: CSS affects all components of same type

## 🎯 Best Practices

### DO:
1. **Work WITH Streamlit's design system**
2. **Use columns for layout**
3. **Use containers for grouping**
4. **Use markdown for text formatting**
5. **Use st.info/st.success/st.warning for callouts**
6. **Keep styling in config.toml**
7. **Use emojis sparingly (they work reliably)**

### DON'T:
1. **Fight Streamlit's defaults**
2. **Use complex CSS selectors**
3. **Try to recreate custom components with CSS**
4. **Mix unsafe_allow_html with Material icons**
5. **Use :contains() or other non-standard CSS**
6. **Override font sizes globally**
7. **Touch arrow/icon rendering**

## 🔧 When You Need More Control

If Streamlit can't achieve your design needs, consider:

1. **Streamlit Components**: Build custom React components
2. **Dash**: Python with full CSS/HTML control
3. **Gradio**: Simpler but cleaner than Streamlit
4. **FastAPI + Frontend**: Full control but more complex
5. **Panel**: More customizable Python framework

## 🚨 Debug Checklist

When things break:
1. Remove ALL custom CSS first
2. Check if using `unsafe_allow_html=True` with icons
3. Update Streamlit to latest version
4. Clear browser cache
5. Test without any styling
6. Add back config.toml colors only
7. Use native Streamlit components for structure

## 💡 Key Insight

**Streamlit is designed to be simple and consistent, not infinitely customizable. The moment you fight against its design philosophy with CSS, things break. Embrace its constraints or choose a different framework.**

---

*Last Updated: 2025-09-29*
*Based on Streamlit behavior through 2024/2025 releases*