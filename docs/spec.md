# Winner Bot – Ultimate Master Spec (Final Version with Contact & Terms)

## Repository Structure

```
/bot/                  # Backend Python bot
    bot.py
    config.json
    strategies/
        rsi_extreme.py
        macd_cross.py
        ema_crossover.py
        bollinger_band.py
        volume_spike.py
        pattern_recognition.py
        ai_stability_detector.py
        enabled.py
    utils/             # Helpers like get_candles()
    alerts/            # Notification function for app only
    logging/           # Excel/CSV + rotating logs
/frontend/             # Flutter or React Native mobile app
    lib/
    android/
    ios/               # Optional
/dashboard/            # Web-based dashboards
    user_dashboard/
    admin_dashboard/
/docs/
    spec.md            # Full project spec
    terms.md           # Terms & Conditions
    privacy.md         # Privacy Policy
    contact.md         # Contact information
/.github/workflows/
    ci.yml             # CI/CD automation
/assets/
    logo.png
    graphics/
/auth/                 # Email OTP login
.env.example
README.md
```

## Backend Bot Features

- All strategies included: RSI, MACD, EMA, Bollinger, Volume Spike, Pattern Recognition, AI Stability Detector
- High-Confirmation Mode (≥2 strategies must agree)
- High accuracy signals (80–90%)
- Supports all live + OTC pairs
- Timeframes: 1m, 5m, 15m
- Live chart reading with real candles
- Scheduler runs per user-selected timeframe
- Logging: Excel/CSV + rotating logs
- Config-driven for pairs, strategies, thresholds
- Semi-auto GUI optional for admin testing

## User Features

- Login with email OTP
- 7-day free trial
- Subscription plans: Monthly $15 USD / Lifetime $150 USD
- Auto-block if subscription expires; auto-unblock if payment detected
- Payment via Binance Wallet: TYhJZueqsDrR5iUSMjV5YT67qPohg8LYbE
- Users can manually select timeframe and pairs
- Single in-app notification per signal
- Dashboard: live chart + signals + accuracy per pair
- Live candles 24/7 (live + OTC)
- Contact page with support email/phone
- Terms & Conditions
- Privacy Policy

## Admin Features

- Admin email: chaudreyadnan@gmail.com
- Full access: strategies, pairs, thresholds, users, subscriptions, logs, live charts
- Monitor: live signals, user activity, accuracy, notifications
- Can view Contact, Terms, Privacy sections as reference

## Mobile / Web Frontend

### User Dashboard

- Live signals table
- Live candle charts (all pairs)
- Accuracy display per pair
- Timeframe selector: 1m / 5m / 15m → updates all signals
- Single notification per signal
- Contact, Terms & Privacy accessible from dashboard

### Admin Dashboard

- Manage strategies, thresholds, pairs
- View logs, signal accuracy, user activity
- Manage subscriptions (auto-block/unblock)
- Deploy updates

### Graphics & Design

- Professional logo and graphics
- Clean, modern, responsive UI
- Optional dark/light mode
- Looks similar to Quotex style

### App Build

- Android APK / AAB ready for Play Store
- Only displays signals (no auto-trading)

## REST API

- `/signals/latest` → JSON with latest signals per pair & timeframe
- `/signals/history` → JSON/CSV for past signals
- `/user/status` → subscription & trial status
- `/admin/metrics` → dashboard metrics
- `/contact`, `/terms`, `/privacy` endpoints
- Secured via API key in `.env`

## CI/CD

- GitHub Actions: test backend, build APK/AAB, generate backend ZIP
- Automatic artifacts for download
- PR optional for updates

## Secrets / .env Variables

```
ADMIN_EMAIL="chaudreyadnan@gmail.com"
EMAIL_APP_PASSWORD=""
API_KEY=""               # For REST API
FIREBASE_KEY=""          # Push notifications
USER_WALLET_ADDRESS="TYhJZueqsDrR5iUSMjV5YT67qPohg8LYbE"  # Reference only
BINANCE_API_KEY=""       # Optional for payments
BINANCE_SECRET_KEY=""    # Optional for payments
```

## Notes

- All secrets handled via `.env` and GitHub secrets; no hardcoding.
- Create all folders and files automatically according to repo structure.
- Fully functional, hands-off; future updates via natural language instructions.
- High-Confirmation, high accuracy. User login, subscription, auto-block/unblock. Live + OTC candles. Dashboard with accuracy, timeframe selection, single notification. Admin access and email alerts. Professional graphics & logo. Contact, Terms, Privacy sections.