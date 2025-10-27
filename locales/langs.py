# Supported languages (code, native name)
LANGS = [
    ('en', 'English'),
    ('tr', 'Türkçe'),
    ('es', 'Español'),
    ('fr', 'Français'),
    ('de', 'Deutsch'),
    ('ru', 'Русский'),
    ('ar', 'العربية'),
    ('zh', '中文'),
    ('hi', 'हिन्दी'),
    ('pt', 'Português'),
    ('ja', '日本語'),
    ('ko', '한국어'),
    ('it', 'Italiano'),
    ('nl', 'Nederlands'),
    ('pl', 'Polski'),
    ('fa', 'فارسی'),
    ('id', 'Bahasa Indonesia'),
    ('th', 'ไทย'),
    ('vi', 'Tiếng Việt'),
    ('uk', 'Українська'),
    ('ro', 'Română'),
    ('cs', 'Čeština'),
    ('sv', 'Svenska'),
    ('el', 'Ελληνικά'),
    ('he', 'עברית'),
    ('hu', 'Magyar'),
    ('bn', 'বাংলা'),
    ('ms', 'Bahasa Melayu'),
    ('ta', 'தமிழ்'),
    ('ur', 'اردو'),
]

# Minimal translations for core UI strings
TRANSLATIONS = {
    'en': {
        'connect': 'Connect',
        'refresh_list': 'Refresh List',
        'long': 'LONG',
        'short': 'SHORT',
        'close_all': 'Close All',
        'close_selected': 'Close Selected',
        'auto_trade': 'Auto Trade',
        'save_settings': 'Save Settings',
        'refresh': 'Refresh',
        'pnl_panel': 'Open Trades PNL',
        'summary': 'Summary',
        'positions': 'Open Positions',
        'history': 'Trade History (Realized)',
'log': 'Log',
'license': 'License', 'api': 'API', 'sponsor': 'Sponsor',
        'license_required': 'License required for leverage above 3x.',
        'click_to_buy': 'Click "Get License" to purchase at license.planc.space',
        'pnl_panel': 'Open Trades PNL',
        'market_up': 'Market rising',
        'market_down': 'Market falling',
        'market_neutral': 'Market neutral',
        'symbol_up_suffix': 'rising',
        'symbol_down_suffix': 'falling',
        'symbol_neutral_suffix': 'neutral',
        'env_label': 'Environment (Test/Live):',
        'api_key': 'API Key:',
        'api_secret': 'API Secret:',
        'license_code': 'License Code:',
        'license_status_unlicensed': 'Status: Unlicensed',
        'license_status_active': 'Status: Licensed',
        'license_status_invalid': 'Status: Invalid license',
        'error': 'Error',
        'success': 'Success',
        'info': 'Info',
        'activate': 'Activate',
        'get_license': 'Get License',
        'license_active_btn': 'License Active',
        'account_info': 'Account Info',
        'balance': 'Balance:',
        'connection_status': 'Status:',
        'not_connected': 'Not connected',
        'connected_fmt': 'Connected ✓ ({env})',
        'symbol_label': 'Symbol',
        'selected_coin_info': 'Selected Coin',
        'price': 'Price:',
        'change_24h': 'Change (24h):',
        'trading': 'Trading',
        'trading_mode': 'Trading Mode:',
        'position_size_usdt': 'Position Size (USDT):',
        'leverage_label': 'Leverage:',
        'market_interval_sec': 'Market check interval (s):',
        'target_pnl': 'Target PNL (USDT):',
        'neutral_close_pct_label': 'Neutral Close (%):',
        'auto_balance_pct': 'Auto Balance (%):',
        'stop_loss_pct_label': 'Stop Loss (%):',
        'auto_on': 'Auto Trade: On',
        'auto_off': 'Auto Trade: Off',
'update_available': 'Update Available!',
        'balance_percent_label': 'Balance (%):',
        'help_balance_percent': 'What percentage of your available balance to use per trade.',
        'help_leverage': 'Leverage to set on the selected symbol before opening a position.',
        'help_market_interval': 'How often the market monitor runs (min: 30s due to API rate limits).',
        'help_target_pnl': 'Close the selected symbol when unrealized PNL (USDT) reaches this value.',
        'help_neutral_close_pct': 'When market is neutral, if |24h change| exceeds this %, close the position.',
        'help_auto_balance_pct': 'If >0, use this % of your available USDT per trade.',
        'help_stop_loss_pct': 'If loss reaches this %, automatically close the position.',
        'take_profit_pct_label': 'Take Profit (%):',
        'help_take_profit_pct': 'If profit reaches this %, automatically close the position.',
        'help_market_threshold': 'If rising coins >= this number, market is rising. If falling coins >= this number, market is falling.',
        'help_momentum_threshold': 'If rising coin count drops by this amount, close positions and wait for trend change.',
        'user_guide_btn': 'User Guide',
        'user_guide_title': '📖 User Guide - Crypto Futures Auto Trading Bot',
        'user_guide_content': '''
🚀 WELCOME TO THE CRYPTO FUTURES AUTO TRADING BOT

This program allows you to automatically trade cryptocurrency futures on Binance based on market analysis and momentum.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 TABLE OF CONTENTS:

1️⃣ Getting Started
2️⃣ Getting Binance API Keys
3️⃣ Connecting to Binance
4️⃣ Selecting Coins
5️⃣ Trading Settings
6️⃣ Auto Trading
7️⃣ Risk Management
8️⃣ Monitoring and Logs
9️⃣ FAQ

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ GETTING STARTED

This bot requires:
✓ A Binance account
✓ API keys (API Key + Secret)
✓ USDT balance in your Futures wallet

IMPORTANT NOTES:
⚠️ Start with TEST MODE first!
⚠️ Only use funds you can afford to lose
⚠️ Understand leverage risks before trading
🔒 ONLY USE OFFICIAL LICENSES FROM: https://license.planc.space/
⚠️ UNAUTHORIZED/CRACKED LICENSES CAN CAUSE BOT TO MALFUNCTION!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ GETTING BINANCE API KEYS

STEP 1: Create API Keys
🔗 Go to: https://www.binance.com/en/my/settings/api-management
   1. Log in to your Binance account
   2. Click "Create API" button
   3. Choose "System Generated" or "Third Party App"
   4. Give it a label (e.g., "Trading Bot")
   5. Complete 2FA verification
   6. SAVE your API Key and Secret Key (you'll need them!)

STEP 2: API Permissions
Enable these permissions:
   ✅ Enable Reading
   ✅ Enable Futures
   ❌ Disable Spot & Margin Trading (optional, for safety)
   ❌ Disable Withdrawals (RECOMMENDED for security!)

STEP 3: IP Whitelist (Optional but Recommended)
   - Add your IP address for extra security
   - Leave unrestricted if using dynamic IP

🔗 Binance API Documentation:
   https://www.binance.com/en/support/faq/360002502072

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ CONNECTING TO BINANCE

STEP 1: Select Environment
   🟡 TEST MODE: Use Binance Testnet (no real money)
      • Test URL: https://testnet.binancefuture.com/
      • Get test API keys from testnet
   
   🔴 LIVE MODE: Real trading with real money
      • Use your main Binance API keys
      • Always test strategies in TEST mode first!

STEP 2: Enter API Credentials
   1. Paste your "API Key" in the API Key field
   2. Paste your "Secret Key" in the API Secret field
   3. Click "Connect" button
   4. Wait for "Connected ✓" status

✅ Successful Connection Shows:
   - Your total balance
   - Connected status (green)
   - Coin list loaded

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ SELECTING COINS

METHOD 1: From Available Coins List
   1. Use the search box to find coins
   2. Select 1 or more coins (checkboxes)
   3. Click "Add Selected" button

METHOD 2: Direct Selection
   - Click on any coin card to view details
   - Coins with green background = Rising
   - Coins with red background = Falling

MULTIPLE COINS:
   • You can select up to 20 coins simultaneously
   • Bot will distribute balance across selected coins
   • Example: 100% balance / 5 coins = 20% per coin

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣ TRADING SETTINGS

⚙️ LEVERAGE (1x, 2x, 3x, 5x, 10x, 20x)
   - Multiplier for your position
   - Example: 10x leverage = 10x profit AND 10x loss
   - ⚠️ Higher leverage = Higher risk!
   - Recommended for beginners: 1x - 3x

📊 BALANCE % (1% - 100%)
   - What % of your available balance to use per trade
   - Example: 1000 USDT available, 50% = 500 USDT per trade
   - Recommended: 10% - 30% for safety

⏱️ MARKET CHECK INTERVAL (30s - 600s)
   - How often the bot checks market trends
   - Minimum: 30 seconds (API rate limit protection)
   - Recommended: 60-120 seconds

💰 TARGET PNL (USDT)
   - Auto-close position when profit reaches this amount
   - Example: 50 = close when profit is $50
   - Leave 0 to disable

🛑 STOP LOSS % (1% - 50%)
   - Auto-close position when loss reaches this %
   - Example: 10% = close if loss is -10%
   - ⚠️ ALWAYS USE STOP LOSS!
   - Recommended: 5% - 15%

🎯 TAKE PROFIT % (1% - 100%)
   - Auto-close position when profit reaches this %
   - Example: 20% = close if profit is +20%
   - Recommended: 10% - 30%

⚡ MOMENTUM LOSS THRESHOLD (1 - 20)
   - How many coins must change direction to close positions
   - Example: 3 = if 3+ rising coins turn falling, close LONG
   - Recommended: 3 - 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6️⃣ AUTO TRADING

🤖 HOW IT WORKS:

STEP 1: Market Analysis
   - Bot checks Top 100 coins every 4 minutes
   - Counts: Rising vs Falling vs Neutral
   - Determines market trend

STEP 2: Signal Generation
   🟢 MARKET RISING: Opens LONG positions
      • When 60+ coins are rising
   
   🔴 MARKET FALLING: Opens SHORT positions
      • When 60+ coins are falling
   
   ⚪ MARKET NEUTRAL: No action or close positions
      • When market is unclear

STEP 3: Position Management
   ✅ Auto-opens positions based on market trend
   ✅ Manages stop loss and take profit
   ✅ Closes positions when momentum is lost
   ✅ Adjusts leverage automatically

STARTING AUTO TRADE:
   1. Select coins you want to trade
   2. Set your trading parameters
   3. Click ">> Auto Trade" button
   4. Status changes to "Auto Trade: On"

STOPPING AUTO TRADE:
   - Click ">> Auto Trade" button again
   - Status changes to "Auto Trade: Off"
   - Open positions remain (manually close if needed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7️⃣ RISK MANAGEMENT

⚠️ MOMENTUM LOSS PROTECTION:
   When market momentum changes suddenly:
   1. Bot detects rising coins dropping by threshold
   2. Automatically closes ALL positions
   3. Pauses trading until trend reverses completely
   4. Protects you from big losses

📊 POSITION MONITORING:
   • Check "Open Positions" tab regularly
   • Monitor your PNL (Profit/Loss)
   • Watch for leverage liquidation risks

🛡️ SAFETY TIPS:
   ✅ Always use Stop Loss
   ✅ Don't risk more than 5% of capital per trade
   ✅ Start with low leverage (1x-3x)
   ✅ Test strategies in TEST mode first
   ✅ Never leave bot running unattended for long periods
   ✅ Monitor your positions regularly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8️⃣ MONITORING AND LOGS

📈 ACCOUNT SUMMARY:
   • Toplam PNL: Total profit/loss
   • Total Fee: Trading commissions paid
   • Total Trades: Number of trades executed
   • Long/Short Positions: Currently open positions
   • Total Balance: Your current balance

📊 OPEN POSITIONS:
   - View all active trades
   - See real-time PNL
   - Check entry price and leverage
   - Close individual positions

📝 LOG PANEL:
   - Shows all bot activities
   - Error messages and warnings
   - Trade executions
   - Market trend changes

🔄 REFRESH BUTTONS:
   • [R] Refresh: Update coin prices
   • [≡] Refresh Summary: Update account data
   • [S] Save Settings: Save your configuration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9️⃣ FAQ

Q: Why is my position not opening?
A: Check:
   • API connection is active
   • You have sufficient balance
   • Leverage is supported (3x+ requires license)
   • Market trend is clear (not neutral)

Q: How do I close all positions?
A: Click "[X] Close All Trades" button
   ⚠️ This closes ALL open positions immediately!

Q: What happens if I lose internet connection?
A: 
   • Bot stops working
   • Your positions remain open
   • Stop loss orders stay active (if set)
   • Reconnect ASAP to resume monitoring

Q: Can I run multiple bots?
A: 
   • Yes, but use different API keys
   • Or use different accounts
   • Don't trade same coins on multiple bots

Q: How much profit can I expect?
A: 
   • Profits vary based on market conditions
   • Past performance ≠ future results
   • Always be prepared for losses
   • Crypto markets are highly volatile

Q: Do I need a license?
A: 
   • No license: 1x leverage only
   • With license: Up to 20x leverage
   • Get license at: https://license.planc.space/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT DISCLAIMERS:

1. This bot does NOT guarantee profits
2. Crypto trading carries high risk
3. Only invest what you can afford to lose
4. Past results do not predict future performance
5. You are responsible for your trading decisions
6. Always use stop loss protection
7. Start with small amounts and TEST mode
8. Monitor your positions regularly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆘 NEED HELP?

📧 Support: support@planc.space
🌐 Website: https://planc.space
📜 License: https://license.planc.space

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Good luck with your trading! 🚀💰
''',
        # Additional translations
        'env_test': 'Test',
        'env_live': 'Live',
        'search_label': 'Search:',
        'selected_count': 'Selected: {count} coin(s)',
        'add_selected': 'Add Selected',
        'remove_selected': 'Remove Selected',
        'multi_coin_selection': 'Multi Coin Selection',
        'market_neutral_text': 'Market neutral',
        'market_rising_text': 'Market rising',
        'market_falling_text': 'Market falling',
        'auto_trade_off_label': 'Auto Trade: Off',
        'auto_trade_on_label': 'Auto Trade: On',
        'mode_test': 'Mode: Test',
        'mode_live': 'Mode: Live',
        'selected_coins_title': 'Selected Coins',
        'account_summary': 'Account Summary',
        'open_positions_title': 'Open Positions',
        'close_all_trades': '[X] Close All Trades',
        'close_selected_trade': '[X] Close Selected',
        'auto_trade_btn': '>> Auto Trade',
        'save_settings_btn': '[S] Save Settings',
        'default_settings_btn': 'Default Settings',
        'refresh_btn': '[R] Refresh',
        'refresh_summary_btn': '[≡] Refresh Summary',
        'update_btn': '[↓] Update',
        'api_keys_required': 'API Key and Secret required!',
        'connect_api_first': 'Please connect to API first!',
        'positions_closed': '{count} position(s) closed!',
        'no_positions_to_close': 'No positions to close.',
        'select_position_from_table': 'Please select a position from the table.',
        'trade_percent_label': 'Trade %:',
        'rising_text': 'Rising',
        'falling_text': 'Falling',
        'neutral_text': 'Neutral',
        'settings_saved': 'Settings saved.',
        'total_pnl_label': 'Total PNL',
        'total_fee_label': 'Total Fee',
        'total_trades_label': 'Total Trades',
        'long_positions_label': 'Long Positions',
        'short_positions_label': 'Short Positions',
        'total_balance_label': 'Total Balance',
        'get_license_btn_text': 'Get License',
        'connect_btn_text': 'Connect',
        'language_label': 'Language / Dil:',
        'api_connection_error': 'API connection error: {error}',
        'disconnect': 'Disconnect',
        # Position table headers
        'position_symbol': 'Symbol',
        'position_side': 'Side',
        'position_size': 'Size',
        'position_entry_price': 'Entry Price',
        'position_leverage': 'Leverage',
        'position_pnl': 'PNL',
        'api_keys_found': 'API keys found, connecting automatically...',
        'api_keys_not_found': 'API keys not found, manual connection required',
        'license_leverage_warning_title': 'License Required',
        'license_leverage_warning_msg': '⚠️ License Required!\n\n🔒 Only 1x leverage is allowed without an active license.\n\n📦 Get a license:\nhttps://license.planc.space/',
        'license_leverage_limited_log': '⚠️ No license, leverage limited to 1x',
        'close_positions_warning_title': 'Open Positions',
        'close_positions_warning_msg': '⚠️ You have {count} open position(s)!\n\nPlease close your positions manually before exiting the program.',
        'coin_list_loading': 'Loading coin list...',
        'coin_removed': 'Coin removed: {symbol}',
        'coin_added': 'Coin added: {symbol}',
        'updating_cards': 'Updating {count} card(s)',
        'no_change_data': 'No change data available',
        'fetching_data': 'Fetching data...',
        'account_data_fetching': 'Fetching account data...',
        'update_module_not_loaded': 'Update module could not be loaded.',
        'checking_updates': 'Checking for updates...',
        'update_check_error': 'Update check error: {error}',
        'update_check_failed': 'Update check could not be started: {error}',
        'update_dialog_error': 'Update dialog could not be shown: {error}',
        # Updater translations
        'software_update_title': 'Software Update',
        'new_update_available': '🔄 New Update Available!',
        'ready': 'Ready...',
        'update': 'Update',
        'cancel': 'Cancel',
        'software_uptodate': '✅ Software Up to Date',
        'ok': 'OK',
        'close_program_btn': 'Close Program',
        'update_completed': 'Update Completed',
        'program_will_restart': 'Program will restart.',
        'update_error_title': 'Update Error',
        'update_available_title': 'Update Available',
        'commit_info_failed': 'Could not get commit information',
        'local_git_info_failed': 'Could not get local git information',
        'version_info_failed': 'Could not get version information from GitHub',
        'new_update_message': 'New update available: {message}',
        'software_is_uptodate': 'Software is up to date',
        'update_check_error_msg': 'Update check error: {error}',
        'downloading_update': 'Downloading update...',
        'extracting_archive': 'Extracting archive...',
        'updating_files': 'Updating files...',
        'update_complete': 'Update complete!',
        'update_error_msg': 'Update error: {error}',
        'files_updated': '{count} files updated',
        'trader_bot_ai': 'TRADER BOT AI',
        'crypto_news': 'Crypto News',
        'market_threshold_label': 'Market Trend Threshold',
        'momentum_threshold_label': 'Momentum Loss Threshold',
        'stop_loss_coin_label': 'Stop Loss:',
        'refreshing': 'Refreshing...',
        'license_status_active_short': 'Status: License Active',
        'ok_button': 'OK',
        'force_close_button': 'Close Anyway',
        'trade_percent': 'Trade %:',
        'trade_percent_label': 'Trade %:',
        'take_profit_pct_label': 'Take Profit (%):',
    },
    'tr': {
        'connect': 'Bağlan',
        'refresh_list': 'Listeyi Yenile',
        'long': 'LONG',
        'short': 'SHORT',
        'close_all': 'Tümünü Kapat',
        'close_selected': 'Seçiliyi Kapat',
        'auto_trade': 'Oto Trade',
        'save_settings': 'Ayarları Kaydet',
        'refresh': 'Yenile',
        'pnl_panel': 'Açık İşlemler PNL',
        'summary': 'Özet',
        'positions': 'Açık Pozisyonlar',
        'history': 'Geçmiş İşlemler (Realized)',
'log': 'Log',
'license': 'Lisans', 'api': 'API', 'sponsor': 'Sponsor',
        'license_required': '3x üzeri kaldıraç için lisans gerekli.',
        'click_to_buy': 'Satın almak için "Lisans Al"a tıklayın: license.planc.space',
        'market_up': 'Piyasa yükseliyor',
        'market_down': 'Piyasa düşüyor',
        'market_neutral': 'Piyasa nötr',
        'symbol_up_suffix': 'yükseliyor',
        'symbol_down_suffix': 'düşüyor',
        'symbol_neutral_suffix': 'nötr',
        'env_label': 'Ortam (Test/Gerçek):',
        'language_label': 'Dil / Language:',
        'api_key': 'API Key:',
        'api_secret': 'API Secret:',
        'license_code': 'Lisans Kodu:',
        'license_status_unlicensed': 'Durum: Lisanssız',
        'license_status_active': 'Durum: Lisans Aktif',
        'license_status_invalid': 'Durum: Geçersiz Lisans',
        'error': 'Hata',
        'success': 'Başarılı',
        'info': 'Bilgi',
        'activate': 'Etkinleştir',
        'get_license': 'Lisans Al',
        'license_active_btn': 'Lisans Aktif',
        'account_info': 'Hesap Bilgileri',
        'balance': 'Bakiye:',
        'connection_status': 'Durum:',
        'not_connected': 'Bağlı değil',
        'connected_fmt': 'Bağlandı ✓ ({env})',
        'symbol_label': 'Sembol',
        'selected_coin_info': 'Seçili Coin Bilgisi',
        'price': 'Fiyat:',
        'change_24h': 'Değişim (24h):',
        'trading': 'İşlem',
        'trading_mode': 'İşlem Modu:',
        'position_size_usdt': 'Pozisyon Boyutu (USDT):',
        'leverage_label': 'Kaldıraç:',
        'market_interval_sec': 'Piyasa kontrol süresi (sn):',
        'target_pnl': 'Hedef PNL (USDT):',
        'neutral_close_pct_label': 'Nötr Kapat (%):',
        'auto_balance_pct': 'Oto Bakiye (%):',
        'stop_loss_pct_label': 'Zarar Durdur (%):',
        'auto_on': 'Oto Trade: Açık',
        'auto_off': 'Oto Trade: Kapalı',
'update_available': 'Güncelleme Bekliyor!',
        'balance_percent_label': 'Bakiye (%):',
        'help_balance_percent': 'Her işlemde kullanılabilir bakiyenizin yüzde kaçını kullanmak istiyorsunuz.',
        'help_leverage': 'Pozisyon açmadan önce seçili sembole ayarlanacak kaldıraç.',
        'help_market_interval': 'Piyasa izleyicinin çalışma aralığı (min: 30sn - API limit koruması).',
        'help_target_pnl': 'Seçili sembolün gerçekleşmemiş PNL (USDT) bu değere ulaşınca kapat.',
        'help_neutral_close_pct': 'Piyasa nötrken |24s değişim| bu yüzdeyi aşarsa pozisyonu kapat.',
        'help_auto_balance_pct': '0\'dan büyükse, her işlemde müsait USDT bakiyenizin bu yüzdesi kullanılır.',
        'help_stop_loss_pct': 'Zarar bu yüzdeye ulaşınca pozisyonu otomatik kapat.',
        'take_profit_pct_label': 'Kar Al (%):',
        'help_take_profit_pct': 'Kar bu yüzdeye ulaşınca pozisyonu otomatik kapat.',
        'help_market_threshold': 'Yükselen coin sayısı >= bu sayı ise piyasa yükseliyor. Düşen coin sayısı >= bu sayı ise piyasa düşüyor.',
        'help_momentum_threshold': 'Yükselen coin sayısı bu kadar düşerse pozisyonları kapat ve trend değişimi bekle.',
        'user_guide_btn': 'Kullanım Kılavuzu',
        'user_guide_title': '📖 Kullanım Kılavuzu - Kripto Futures Otomatik Trading Botu',
        'user_guide_content': '''
🚀 KRİPTO FUTURES OTOMATİK TRADING BOTUNA HOŞGELDİNİZ

Bu program, Binance'de piyasa analizi ve momentuma dayalı olarak otomatik kripto vadeli işlem yapmanızı sağlar.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 İÇİNDEKİLER:

1️⃣ Başlarken
2️⃣ Binance API Anahtarları Nasıl Alınır
3️⃣ Binance'e Bağlanma
4️⃣ Coin Seçimi
5️⃣ Trading Ayarları
6️⃣ Otomatik Trading
7️⃣ Risk Yönetimi
8️⃣ İzleme ve Loglar
9️⃣ Sık Sorulan Sorular

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ BAŞLARKEN

Bu bot için gerekenler:
✓ Binance hesabı
✓ API anahtarları (API Key + Secret)
✓ Futures cüzdanında USDT bakiyesi

ÖNEMLİ NOTLAR:
⚠️ Önce TEST MODDA başlayın!
⚠️ Sadece kaybetmeyi göze alabileceğiniz fonları kullanın
⚠️ İşlem yapmadan önce kaldıraç risklerini anlayın
🔒 SADECE RESMİ LİSANS KULLANIN: https://license.planc.space/
⚠️ YETKİSİZ/CRACK LİSANSLAR BOT'UN YANLIŞ İŞLEM AÇMASINA NEDEN OLABİLİR!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ BİNANCE API ANAHTARLARI NASIL ALINIR

ADIM 1: API Anahtarları Oluşturma
🔗 Gidin: https://www.binance.com/tr/my/settings/api-management
   1. Binance hesabınıza giriş yapın
   2. "API Oluştur" butonuna tıklayın
   3. "Sistem Tarafından Oluşturulan" veya "Üçüncü Taraf Uygulama" seçin
   4. Bir etiket verin (örn: "Trading Botu")
   5. 2FA doğrulamasını tamamlayın
   6. API Key ve Secret Key'inizi KAYDEDIN (ihtiyacınız olacak!)

ADIM 2: API İzinleri
Bu izinleri etkinleştirin:
   ✅ Okuma'yı Etkinleştir
   ✅ Futures'ı Etkinleştir
   ❌ Spot & Margin Trading'i Devre Dışı Bırakın (güvenlik için)
   ❌ Çekim İşlemlerini Devre Dışı Bırakın (GÜVENLİK İÇİN ÖNERİLİR!)

ADIM 3: IP Beyaz Listesi (İsteğe Bağlı ama Önerilir)
   - Ekstra güvenlik için IP adresinizi ekleyin
   - Dinamik IP kullanıyorsanız kısıtlamasız bırakın

🔗 Binance API Dokümantasyonu:
   https://www.binance.com/tr/support/faq/360002502072

🔗 Test API Anahtarları (Test Modu için):
   https://testnet.binancefuture.com/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ BİNANCE'E BAĞLANMA

ADIM 1: Ortam Seçimi
   🟡 TEST MODU: Binance Testnet kullanın (gerçek para yok)
      • Test URL: https://testnet.binancefuture.com/
      • Testnet'ten test API anahtarları alın
   
   🔴 CANLI MOD: Gerçek para ile gerçek işlem
      • Ana Binance API anahtarlarınızı kullanın
      • Stratejileri önce TEST modda deneyin!

ADIM 2: API Bilgilerini Girin
   1. "API Key" alanına API Key'inizi yapıştırın
   2. "API Secret" alanına Secret Key'inizi yapıştırın
   3. "Bağlan" butonuna tıklayın
   4. "Bağlandı ✓" durumunu bekleyin

✅ Başarılı Bağlantı Gösterir:
   - Toplam bakiyeniz
   - Bağlandı durumu (yeşil)
   - Coin listesi yüklendi

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ COİN SEÇİMİ

YÖNTEM 1: Mevcut Coin Listesinden
   1. Coin bulmak için arama kutusunu kullanın
   2. 1 veya daha fazla coin seçin (checkboxlar)
   3. "Seçilenleri Ekle" butonuna tıklayın

YÖNTEM 2: Doğrudan Seçim
   - Detayları görmek için herhangi bir coin kartına tıklayın
   - Yeşil arka planlı coinler = Yükseliyor
   - Kırmızı arka planlı coinler = Düşüyor

ÇOKLU COİNLER:
   • Aynı anda 20'ye kadar coin seçebilirsiniz
   • Bot bakiyeyi seçilen coinlere dağıtır
   • Örnek: %100 bakiye / 5 coin = coin başına %20

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣ TRADING AYARLARI

⚙️ KALDIRAÇ (1x, 2x, 3x, 5x, 10x, 20x)
   - Pozisyonunuz için çarpan
   - Örnek: 10x kaldıraç = 10x kar VE 10x zarar
   - ⚠️ Yüksek kaldıraç = Yüksek risk!
   - Yeni başlayanlar için önerilen: 1x - 3x

📊 BAKİYE % (1% - 100%)
   - İşlem başına kullanılabilir bakiyenizin yüzde kaçı kullanılacak
   - Örnek: 1000 USDT mevcut, %50 = işlem başına 500 USDT
   - Önerilen: Güvenlik için %10 - %30

⏱️ PİYASA KONTROL ARALIĞI (30s - 600s)
   - Bot'un piyasa trendlerini ne sıklıkla kontrol ettiği
   - Minimum: 30 saniye (API rate limit koruması)
   - Önerilen: 60-120 saniye

💰 HEDEF PNL (USDT)
   - Kar bu miktara ulaştığında pozisyonu otomatik kapat
   - Örnek: 50 = kar $50 olduğunda kapat
   - Devre dışı bırakmak için 0 bırakın

🛑 ZARAR DURDUR % (1% - 50%)
   - Zarar bu %'ye ulaştığında pozisyonu otomatik kapat
   - Örnek: %10 = zarar -10% olduğunda kapat
   - ⚠️ DAIMA ZARAR DURDUR KULLANIN!
   - Önerilen: %5 - %15

🎯 KAR AL % (1% - 100%)
   - Kar bu %'ye ulaştığında pozisyonu otomatik kapat
   - Örnek: %20 = kar +20% olduğunda kapat
   - Önerilen: %10 - %30

⚡ MOMENTUM KAYBI EŞİĞİ (1 - 20)
   - Kaç coin yön değiştirdiğinde pozisyonlar kapatılacak
   - Örnek: 3 = 3+ yükselen coin düşerse, LONG'ları kapat
   - Önerilen: 3 - 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6️⃣ OTOMATİK TRADING

🤖 NASIL ÇALIŞIR:

ADIM 1: Piyasa Analizi
   - Bot her 4 dakikada Top 100 coini kontrol eder
   - Sayar: Yükselen vs Düşen vs Nötr
   - Piyasa trendini belirler

ADIM 2: Sinyal Üretimi
   🟢 PİYASA YÜKSELİYOR: LONG pozisyonları açar
      • 60+ coin yükseliyorken
   
   🔴 PİYASA DÜŞÜYOR: SHORT pozisyonları açar
      • 60+ coin düşerken
   
   ⚪ PİYASA NÖTR: İşlem yapmaz veya pozisyonları kapatır
      • Piyasa belirsizken

ADIM 3: Pozisyon Yönetimi
   ✅ Piyasa trendine göre otomatik pozisyon açar
   ✅ Zarar durdur ve kar al'ı yönetir
   ✅ Momentum kaybında pozisyonları kapatır
   ✅ Kaldıracı otomatik ayarlar

OTO TRADE BAŞLATMA:
   1. İşlem yapmak istediğiniz coinleri seçin
   2. Trading parametrelerinizi ayarlayın
   3. ">> Oto Trade" butonuna tıklayın
   4. Durum "Oto Trade: Açık" olarak değişir

OTO TRADE DURDURMA:
   - ">> Oto Trade" butonuna tekrar tıklayın
   - Durum "Oto Trade: Kapalı" olarak değişir
   - Açık pozisyonlar kalır (gerekirse manuel kapatın)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7️⃣ RİSK YÖNETİMİ

⚠️ MOMENTUM KAYBI KORUNASI:
   Piyasa momentumu aniden değiştiğinde:
   1. Bot yükselen coinlerin eşik kadar düştüğünü tespit eder
   2. Otomatik olarak TÜM pozisyonları kapatır
   3. Trend tamamen dönene kadar trading'i duraklatır
   4. Sizi büyük kayıplardan korur

📊 POZİSYON İZLEME:
   • "Açık Pozisyonlar" sekmesini düzenli kontrol edin
   • PNL'inizi (Kâr/Zarar) izleyin
   • Kaldıraç likidasyonu risklerini gözleyin

🛡️ GÜVENLİK İPUÇLARI:
   ✅ Daima Zarar Durdur kullanın
   ✅ İşlem başına sermayenin %5'inden fazla risk almayın
   ✅ Düşük kaldıraçla başlayın (1x-3x)
   ✅ Stratejileri önce TEST modda deneyin
   ✅ Botu uzun süre gözetimsiz bırakmayın
   ✅ Pozisyonlarınızı düzenli izleyin

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8️⃣ İZLEME VE LOGLAR

📈 HESAP ÖZETİ:
   • Toplam PNL: Toplam kâr/zarar
   • Toplam Fee: Ödenen işlem komisyonları
   • Toplam İşlem: Gerçekleştirilen işlem sayısı
   • Long/Short Pozisyon: Şu anda açık pozisyonlar
   • Toplam Bakiye: Mevcut bakiyeniz

📊 AÇIK POZİSYONLAR:
   - Tüm aktif işlemleri görüntüleyin
   - Gerçek zamanlı PNL görün
   - Giriş fiyatı ve kaldıracı kontrol edin
   - Bireysel pozisyonları kapatın

📝 LOG PANELİ:
   - Tüm bot aktivitelerini gösterir
   - Hata mesajları ve uyarılar
   - İşlem gerçekleştirmeleri
   - Piyasa trendi değişimleri

🔄 YENİLEME BUTONLARI:
   • [R] Yenile: Coin fiyatlarını güncelle
   • [≡] Özet Yenile: Hesap verilerini güncelle
   • [S] Ayarları Kaydet: Yapılandırmanızı kaydet

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9️⃣ SIK SORULAN SORULAR

S: Pozisyonum neden açılmıyor?
C: Kontrol edin:
   • API bağlantısı aktif mi
   • Yeterli bakiyeniz var mı
   • Kaldıraç destekleniyor mu (3x+ lisans gerektirir)
   • Piyasa trendi açık mı (nötr değil)

S: Tüm pozisyonları nasıl kapatırım?
C: "[X] Tüm İşlemleri Kapat" butonuna tıklayın
   ⚠️ Bu TÜM açık pozisyonları anında kapatır!

S: İnternet bağlantımı kaybedersem ne olur?
C: 
   • Bot çalışmayı durdurur
   • Pozisyonlarınız açık kalır
   • Zarar durdur emirleri aktif kalır (ayarlandıysa)
   • İzlemeye devam etmek için EN KISA SÜREDE yeniden bağlanın

S: Birden fazla bot çalıştırabilir miyim?
C: 
   • Evet, ama farklı API anahtarları kullanın
   • Veya farklı hesaplar kullanın
   • Aynı coinleri birden fazla botta işlem yapmayın

S: Ne kadar kâr bekleyebilirim?
C: 
   • Kârlar piyasa koşullarına göre değişir
   • Geçmiş performans ≠ gelecek sonuçlar
   • Daima kayıplara hazır olun
   • Kripto piyasaları son derece volatildir

S: Lisansa ihtiyacım var mı?
C: 
   • Lisans yok: Sadece 1x kaldıraç
   • Lisans ile: 20x'e kadar kaldıraç
   • Lisans almak için: https://license.planc.space/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ ÖNEMLİ UYARILAR:

1. Bu bot kâr garantisi VERMEZ
2. Kripto işlemleri yüksek risk taşır
3. Sadece kaybetmeyi göze alabileceğiniz parayı yatırın
4. Geçmiş sonuçlar gelecek performansı tahmin etmez
5. İşlem kararlarınızdan siz sorumlusunuz
6. Daima zarar durdur koruması kullanın
7. Küçük miktarlarla ve TEST moduyla başlayın
8. Pozisyonlarınızı düzenli olarak izleyin

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆘 YARDIMA MI İHTİYACINIZ VAR?

📧 Destek: support@planc.space
🌐 Website: https://planc.space
📜 Lisans: https://license.planc.space

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

İyi tradeler! 🚀💰
''',
        # Ek çeviriler
        'env_test': 'Test',
        'env_live': 'Gerçek',
        'search_label': 'Ara:',
        'selected_count': 'Seçili: {count} coin',
        'add_selected': 'Seçilenleri Ekle',
        'remove_selected': 'Seçilenleri Çıkar',
        'multi_coin_selection': 'Çoklu Coin Seçimi',
        'market_neutral_text': 'Piyasa nötr',
        'market_rising_text': 'Piyasa yükselişte',
        'market_falling_text': 'Piyasa düşüşte',
        'auto_trade_off_label': 'Oto Trade: Kapalı',
        'auto_trade_on_label': 'Oto Trade: Açık',
        'mode_test': 'Mod: Test',
        'mode_live': 'Mod: Gerçek',
        'selected_coins_title': 'Seçilen Coinler',
        'account_summary': 'Hesap Özeti',
        'open_positions_title': 'Açık Pozisyonlar',
        'close_all_trades': '[X] Tüm İşlemleri Kapat',
        'close_selected_trade': '[X] Seçiliyi Kapat',
        'auto_trade_btn': '>> Oto Trade',
        'save_settings_btn': '[S] Ayarları Kaydet',
        'default_settings_btn': 'Varsayılan Ayarlar',
        'refresh_btn': '[R] Yenile',
        'refresh_summary_btn': '[≡] Özet Yenile',
        'update_btn': '[↓] Güncelle',
        'api_keys_required': 'API Key ve Secret gerekli!',
        'connect_api_first': 'Önce API\'ye bağlanın!',
        'positions_closed': '{count} pozisyon kapatıldı!',
        'no_positions_to_close': 'Kapatılacak pozisyon yok.',
        'select_position_from_table': 'Lütfen tablodan bir pozisyon seçin.',
        'trade_percent_label': 'İşlem %:',
        'rising_text': 'Yükseliyor',
        'falling_text': 'Düşüyor',
        'neutral_text': 'Nötr',
        'settings_saved': 'Ayarlar kaydedildi.',
        'total_pnl_label': 'Toplam PNL',
        'total_fee_label': 'Toplam Fee',
        'total_trades_label': 'Toplam İşlem',
        'long_positions_label': 'Long Pozisyon',
        'short_positions_label': 'Short Pozisyon',
        'total_balance_label': 'Toplam Bakiye',
        'get_license_btn_text': 'Lisans Al',
        'connect_btn_text': 'Bağlan',
        'language_label': 'Dil / Language:',
        'api_connection_error': 'API bağlantı hatası: {error}',
        'disconnect': 'Bağlantıyı Kes',
        # Position table headers
        'position_symbol': 'Sembol',
        'position_side': 'Yön',
        'position_size': 'Miktar',
        'position_entry_price': 'Giriş Fiyatı',
        'position_leverage': 'Kaldıraç',
        'position_pnl': 'K/Z',
        'api_keys_found': 'API anahtarları bulundu, otomatik bağlantı kuruluyor...',
        'api_keys_not_found': 'API anahtarları bulunamadı, manuel bağlantı gerekli',
        'license_leverage_warning_title': 'Lisans Gerekli',
        'license_leverage_warning_msg': '⚠️ Lisans Gerekli!\n\n🔒 Aktif lisans olmadan sadece 1x kaldıraç kullanılabilir.\n\n📦 Lisans almak için:\nhttps://license.planc.space/',
        'license_leverage_limited_log': '⚠️ Lisans yok, kaldıraç 1x ile sınırlandırıldı',
        'close_positions_warning_title': 'Açık Pozisyonlar',
        'close_positions_warning_msg': '⚠️ {count} adet açık pozisyonunuz var!\n\nLütfen programdan çıkmadan önce pozisyonlarınızı manuel olarak kapatın.',
        'coin_list_loading': 'Coin listesi yükleniyor...',
        'coin_removed': 'Coin çıkarıldı: {symbol}',
        'coin_added': 'Coin eklendi: {symbol}',
        'updating_cards': '{count} kutucuk güncelleniyor',
        'no_change_data': 'Değişim verisi bulunamadı',
        'fetching_data': 'Veriler çekiliyor...',
        'account_data_fetching': 'Hesap verileri çekiliyor...',
        'update_module_not_loaded': 'Güncelleme modülü yüklenemedi.',
        'checking_updates': 'Güncelleme kontrol ediliyor...',
        'update_check_error': 'Güncelleme kontrolü hatası: {error}',
        'update_check_failed': 'Güncelleme kontrolü başlatılamadı: {error}',
        'update_dialog_error': 'Güncelleme diyaloğu gösterilemedi: {error}',
        # Updater çevirileri
        'software_update_title': 'Yazılım Güncellemesi',
        'new_update_available': '🔄 Yeni Güncelleme Mevcut!',
        'ready': 'Hazır...',
        'update': 'Güncelle',
        'cancel': 'İptal',
        'software_uptodate': '✅ Yazılım Güncel',
        'ok': 'Tamam',
        'close_program_btn': 'Programı Kapat',
        'update_completed': 'Güncelleme Tamamlandı',
        'program_will_restart': 'Program yeniden başlatılacak.',
        'update_error_title': 'Güncelleme Hatası',
        'update_available_title': 'Güncelleme Mevcut',
        'commit_info_failed': 'Commit bilgisi alınamadı',
        'local_git_info_failed': 'Yerel git bilgisi alınamadı',
        'version_info_failed': 'GitHub\'dan versiyon bilgisi alınamadı',
        'new_update_message': 'Yeni güncelleme mevcut: {message}',
        'software_is_uptodate': 'Yazılım güncel',
        'update_check_error_msg': 'Güncelleme kontrolü hatası: {error}',
        'downloading_update': 'Güncelleme indiriliyor...',
        'extracting_archive': 'Arşiv açılıyor...',
        'updating_files': 'Dosyalar güncelleniyor...',
        'update_complete': 'Güncelleme tamamlandı!',
        'update_error_msg': 'Güncelleme hatası: {error}',
        'update_restart_required': 'Program yeniden başlatılıyor...',
        'update_will_complete_on_restart': 'Güncelleme tamamlanacak. Programı tekrar açın.',
        'update_file_locked': '{count} dosya kilitli. Güncelleme yeniden başlatma sonrası tamamlanacak.',
        'files_updated': '{count} dosya güncellendi',
        'trader_bot_ai': 'TRADER BOT AI',
        'crypto_news': 'Kripto Haberleri',
        'market_threshold_label': 'Piyasa Trend Eşiği',
        'momentum_threshold_label': 'Momentum Kaybı Eşiği',
        'stop_loss_coin_label': 'Stop Loss:',
        'refreshing': 'Yenileniyor...',
        'license_status_active_short': 'Durum: Lisans Aktif',
        'ok_button': 'Tamam',
        'force_close_button': 'Yine de Kapat',
        'trade_percent': 'İşlem %:',
        'trade_percent_label': 'İşlem %:',
        'take_profit_pct_label': 'Kar Al (%):',
    },
    'es': {
        'api': 'API', 'sponsor': 'Patrocinador', 'license': 'Licencia',
        'connect': 'Conectar',
        'refresh_list': 'Actualizar lista',
        'long': 'LONG', 'short': 'SHORT',
        'close_all': 'Cerrar todo', 'close_selected': 'Cerrar seleccionado',
        'auto_trade': 'Auto Trade', 'save_settings': 'Guardar ajustes', 'refresh': 'Actualizar',
        'pnl_panel': 'PNL de operaciones abiertas', 'summary': 'Resumen', 'positions': 'Posiciones abiertas', 'history': 'Historial (Realizado)', 'log': 'Log',
        'trading': 'Operaciones', 'trading_mode': 'Modo de operación:',
        'position_size_usdt': 'Tamaño de posición (USDT):', 'leverage_label': 'Apalancamiento:',
        'market_interval_sec': 'Intervalo de chequeo (s):', 'target_pnl': 'PNL objetivo (USDT):',
        'neutral_close_pct_label': 'Cierre neutral (%):', 'auto_balance_pct': 'Saldo automático (%):',
        'stop_loss_pct_label': 'Stop Loss (%):', 'auto_on': 'Auto Trade: Activado', 'auto_off': 'Auto Trade: Desactivado',
        'account_info': 'Información de la cuenta', 'balance': 'Saldo:', 'connection_status': 'Estado:',
        'not_connected': 'No conectado', 'connected_fmt': 'Conectado ✓ ({env})',
        'symbol_label': 'Símbolo', 'selected_coin_info': 'Moneda seleccionada', 'price': 'Precio:', 'change_24h': 'Cambio (24h):',
        'license_code': 'Código de licencia:', 'license_status_unlicensed': 'Estado: Sin licencia',
        'license_status_active': 'Estado: Con licencia', 'license_status_invalid': 'Estado: Licencia inválida',
        'get_license': 'Comprar licencia', 'license_active_btn': 'Licencia activa',
        'update_available': '¡Actualización disponible!',
        'help_position_size': 'USDT usado para calcular la cantidad.',
        'help_leverage': 'Apalancamiento a aplicar antes de abrir posición.',
        'help_market_interval': 'Cada cuánto se verifica el mercado (segundos).',
        'help_target_pnl': 'Cierra la posición cuando el PNL no realizado (USDT) alcance este valor.',
        'help_neutral_close_pct': 'Con mercado neutral, si |cambio 24h| excede este %, cerrar.',
        'help_auto_balance_pct': 'Si >0, usa este % de tu USDT disponible por operación.',
        'help_stop_loss_pct': 'Si la pérdida alcanza este %, cerrar la posición.',
        'help_momentum_threshold': 'Si el número de monedas en alza cae en esta cantidad, cierra posiciones y espera cambio de tendencia.',
        'user_guide_btn': 'Guía de Uso',
        'market_threshold_label': 'Umbral de Tendencia del Mercado',
        'momentum_threshold_label': 'Umbral de Pérdida de Momentum',
        'stop_loss_coin_label': 'Stop Loss:',
        'trade_percent_label': 'Comercio %:',
        'take_profit_pct_label': 'Tomar Beneficio (%):',
        'default_settings_btn': 'Ajustes Predeterminados',
        'selected_coins_title': 'Monedas Seleccionadas',
        'crypto_news': 'Noticias de Cripto',
        'open_positions_title': 'Posiciones Abiertas',
        'selected_coin_info': 'Moneda Seleccionada',
        'account_summary': 'Resumen de Cuenta',
        'multi_coin_selection': 'Selección de Múltiples Monedas',
        'search_label': 'Buscar:',
        'license_code': 'Código de Licencia:',
        'user_guide_title': '📖 Guía de Uso - Bot de Trading Automático de Futuros Cripto',
        'user_guide_content': '''🚀 BIENVENIDO AL BOT DE TRADING AUTOMÁTICO DE FUTUROS CRIPTO

Este programa te permite operar automáticamente futuros de criptomonedas en Binance basándose en análisis de mercado y momentum.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 TABLA DE CONTENIDOS:

1️⃣ Comenzando
2️⃣ Obtener Claves API de Binance
3️⃣ Conectar a Binance
4️⃣ Seleccionar Monedas
5️⃣ Configuración de Trading
6️⃣ Trading Automático
7️⃣ Gestión de Riesgos
8️⃣ Monitoreo y Registros
9️⃣ Preguntas Frecuentes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ COMENZANDO

Este bot requiere:
✓ Una cuenta de Binance
✓ Claves API (API Key + Secret)
✓ Saldo USDT en tu cartera de Futuros

NOTAS IMPORTANTES:
⚠️ ¡Empieza con el MODO TEST primero!
⚠️ Solo usa fondos que puedas permitirte perder
⚠️ Entiende los riesgos del apalancamiento antes de operar
🔒 SOLO USA LICENCIAS OFICIALES DE: https://license.planc.space/
⚠️ ¡LAS LICENCIAS NO AUTORIZADAS/CRACK PUEDEN CAUSAR MAL FUNCIONAMIENTO DEL BOT!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ OBTENER CLAVES API DE BINANCE

PASO 1: Crear Claves API
🔗 Ve a: https://www.binance.com/es/my/settings/api-management
   1. Inicia sesión en tu cuenta de Binance
   2. Haz clic en el botón "Crear API"
   3. Elige "Generado por el Sistema" o "Aplicación de Terceros"
   4. Dale una etiqueta (ej: "Bot de Trading")
   5. Completa la verificación 2FA
   6. GUARDA tu API Key y Secret Key (¡las necesitarás!)

PASO 2: Permisos API
Habilita estos permisos:
   ✅ Habilitar Lectura
   ✅ Habilitar Futuros
   ❌ Deshabilitar Trading Spot y Margin (opcional, para seguridad)
   ❌ Deshabilitar Retiros (¡RECOMENDADO por seguridad!)

PASO 3: Lista Blanca de IP (Opcional pero Recomendado)
   - Añade tu dirección IP para seguridad extra
   - Deja sin restricción si usas IP dinámica

🔗 Documentación API de Binance:
   https://www.binance.com/en/support/faq/360002502072

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ CONECTAR A BINANCE

PASO 1: Seleccionar Entorno
   🟡 MODO TEST: Usa Binance Testnet (sin dinero real)
      • URL de prueba: https://testnet.binancefuture.com/
      • Obtén claves API de prueba desde testnet
   
   🔴 MODO EN VIVO: Trading real con dinero real
      • Usa tus claves API principales de Binance
      • ¡Siempre prueba estrategias en MODO TEST primero!

PASO 2: Ingresar Credenciales API
   1. Pega tu "API Key" en el campo API Key
   2. Pega tu "Secret Key" en el campo API Secret
   3. Haz clic en el botón "Conectar"
   4. Espera el estado "Conectado ✓"

✅ La Conexión Exitosa Muestra:
   - Tu saldo total
   - Estado conectado (verde)
   - Lista de monedas cargada

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣ SELECCIONAR MONEDAS

MÉTODO 1: Desde Lista de Monedas Disponibles
   1. Usa el cuadro de búsqueda para encontrar monedas
   2. Selecciona 1 o más monedas (casillas)
   3. Haz clic en el botón "Añadir Seleccionado"

MÉTODO 2: Selección Directa
   - Haz clic en cualquier tarjeta de moneda para ver detalles
   - Monedas con fondo verde = Subiendo
   - Monedas con fondo rojo = Bajando

MÚLTIPLES MONEDAS:
   • Puedes seleccionar hasta 20 monedas simultáneamente
   • El bot distribuirá el saldo entre monedas seleccionadas
   • Ejemplo: 100% saldo / 5 monedas = 20% por moneda

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣ CONFIGURACIÓN DE TRADING

⚙️ APALANCAMIENTO (1x, 2x, 3x, 5x, 10x, 20x)
   - Multiplicador para tu posición
   - Ejemplo: apalancamiento 10x = 10x beneficio Y 10x pérdida
   - ⚠️ ¡Mayor apalancamiento = Mayor riesgo!
   - Recomendado para principiantes: 1x - 3x

📊 SALDO % (1% - 100%)
   - Qué % de tu saldo disponible usar por operación
   - Ejemplo: 1000 USDT disponible, 50% = 500 USDT por operación
   - Recomendado: 10% - 30% para seguridad

⏱️ INTERVALO DE REVISIÓN DE MERCADO (30s - 600s)
   - Cada cuánto el bot revisa las tendencias del mercado
   - Mínimo: 30 segundos (protección límite API)
   - Recomendado: 60-120 segundos

💰 PNL OBJETIVO (USDT)
   - Cierre automático de posición cuando el beneficio alcanza esta cantidad
   - Ejemplo: 50 = cerrar cuando el beneficio es $50
   - Dejar 0 para deshabilitar

🛑 STOP LOSS % (1% - 50%)
   - Cierre automático de posición cuando la pérdida alcanza este %
   - Ejemplo: 10% = cerrar si la pérdida es -10%
   - ⚠️ ¡SIEMPRE USA STOP LOSS!
   - Recomendado: 5% - 15%

🎯 TAKE PROFIT % (1% - 100%)
   - Cierre automático de posición cuando el beneficio alcanza este %
   - Ejemplo: 20% = cerrar si el beneficio es +20%
   - Recomendado: 10% - 30%

⚡ UMBRAL DE PÉRDIDA DE MOMENTUM (1 - 20)
   - Cuántas monedas deben cambiar de dirección para cerrar posiciones
   - Ejemplo: 3 = si 3+ monedas en alza se vuelven bajistas, cerrar LONG
   - Recomendado: 3 - 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6️⃣ TRADING AUTOMÁTICO

🤖 CÓMO FUNCIONA:

PASO 1: Análisis de Mercado
   - El bot revisa las Top 100 monedas cada 4 minutos
   - Cuenta: Subiendo vs Bajando vs Neutral
   - Determina la tendencia del mercado

PASO 2: Generación de Señales
   🟢 MERCADO SUBIENDO: Abre posiciones LONG
      • Cuando 60+ monedas están subiendo
   
   🔴 MERCADO BAJANDO: Abre posiciones SHORT
      • Cuando 60+ monedas están bajando
   
   ⚪ MERCADO NEUTRAL: Sin acción o cierra posiciones
      • Cuando el mercado no está claro

PASO 3: Gestión de Posiciones
   ✅ Abre posiciones automáticamente según tendencia de mercado
   ✅ Gestiona stop loss y take profit
   ✅ Cierra posiciones cuando se pierde momentum
   ✅ Ajusta apalancamiento automáticamente

INICIAR TRADING AUTOMÁTICO:
   1. Selecciona monedas que quieras operar
   2. Configura tus parámetros de trading
   3. Haz clic en el botón ">> Trading Automático"
   4. El estado cambia a "Trading Automático: Activado"

DETENER TRADING AUTOMÁTICO:
   - Haz clic en el botón ">> Trading Automático" nuevamente
   - El estado cambia a "Trading Automático: Desactivado"
   - Las posiciones abiertas permanecen (cierra manualmente si es necesario)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7️⃣ GESTIÓN DE RIESGOS

⚠️ PROTECCIÓN DE PÉRDIDA DE MOMENTUM:
   Cuando el momentum del mercado cambia repentinamente:
   1. El bot detecta que las monedas subiendo caen por el umbral
   2. Cierra automáticamente TODAS las posiciones
   3. Pausa el trading hasta que la tendencia se revierta completamente
   4. Te protege de grandes pérdidas

📊 MONITOREO DE POSICIONES:
   • Revisa la pestaña "Posiciones Abiertas" regularmente
   • Monitorea tu PNL (Beneficio/Pérdida)
   • Vigila los riesgos de liquidación por apalancamiento

🛡️ CONSEJOS DE SEGURIDAD:
   ✅ Siempre usa Stop Loss
   ✅ No arriesgues más del 5% del capital por operación
   ✅ Empieza con bajo apalancamiento (1x-3x)
   ✅ Prueba estrategias en MODO TEST primero
   ✅ Nunca dejes el bot funcionando sin supervisión por largos períodos
   ✅ Monitorea tus posiciones regularmente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8️⃣ MONITOREO Y REGISTROS

📈 RESUMEN DE CUENTA:
   • PNL Total: Beneficio/pérdida total
   • Comisión Total: Comisiones de trading pagadas
   • Operaciones Totales: Número de operaciones ejecutadas
   • Posiciones Long/Short: Posiciones actualmente abiertas
   • Saldo Total: Tu saldo actual

📊 POSICIONES ABIERTAS:
   - Ver todas las operaciones activas
   - Ver PNL en tiempo real
   - Ver precio de entrada y apalancamiento
   - Cerrar posiciones individuales

📝 PANEL DE REGISTRO:
   - Muestra todas las actividades del bot
   - Mensajes de error y advertencias
   - Ejecuciones de trading
   - Cambios de tendencia de mercado

🔄 BOTONES DE ACTUALIZACIÓN:
   • [R] Actualizar: Actualizar precios de monedas
   • [≡] Actualizar Resumen: Actualizar datos de cuenta
   • [S] Guardar Configuración: Guardar tu configuración

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9️⃣ PREGUNTAS FRECUENTES

P: ¿Por qué no se abre mi posición?
R: Verifica:
   • La conexión API está activa
   • Tienes saldo suficiente
   • El apalancamiento es compatible (3x+ requiere licencia)
   • La tendencia del mercado es clara (no neutral)

P: ¿Cómo cierro todas las posiciones?
R: Haz clic en el botón "[X] Cerrar Todas las Operaciones"
   ⚠️ ¡Esto cierra TODAS las posiciones abiertas inmediatamente!

P: ¿Qué pasa si pierdo la conexión a internet?
R: 
   • El bot deja de funcionar
   • Tus posiciones permanecen abiertas
   • Las órdenes de stop loss siguen activas (si están configuradas)
   • Reconecta lo antes posible para reanudar el monitoreo

P: ¿Puedo ejecutar múltiples bots?
R: 
   • Sí, pero usa diferentes claves API
   • O usa diferentes cuentas
   • No operes las mismas monedas en múltiples bots

P: ¿Cuánto beneficio puedo esperar?
R: 
   • Los beneficios varían según las condiciones del mercado
   • El rendimiento pasado ≠ resultados futuros
   • Siempre prepárate para pérdidas
   • Los mercados de cripto son muy volátiles

P: ¿Necesito una licencia?
R: 
   • Sin licencia: solo apalancamiento 1x
   • Con licencia: hasta apalancamiento 20x
   • Obtén licencia en: https://license.planc.space/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ DESCARGO IMPORTANTE:

1. Este bot NO garantiza beneficios
2. El trading de cripto conlleva alto riesgo
3. Solo invierte lo que puedas permitirte perder
4. Los resultados pasados no predicen el rendimiento futuro
5. Eres responsable de tus decisiones de trading
6. Siempre usa protección de stop loss
7. Empieza con pequeñas cantidades y MODO TEST
8. Monitorea tus posiciones regularmente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆘 ¿NECESITAS AYUDA?

📧 Soporte: support@planc.space
🌐 Sitio Web: https://planc.space
📜 Licencia: https://license.planc.space

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¡Buena suerte con tu trading! 🚀💰
'''
    },
    'fr': {
        'api': 'API', 'sponsor': 'Sponsor', 'license': 'Licence',
        'connect': 'Connecter', 'refresh_list': 'Rafraîchir la liste',
        'long': 'LONG', 'short': 'SHORT', 'close_all': 'Tout fermer', 'close_selected': 'Fermer la sélection',
        'auto_trade': 'Trading auto', 'save_settings': 'Enregistrer', 'refresh': 'Rafraîchir',
        'pnl_panel': 'PNL des positions ouvertes', 'summary': 'Résumé', 'positions': 'Positions ouvertes', 'history': 'Historique (Réalisé)', 'log': 'Journal',
        'trading': 'Trading', 'trading_mode': 'Mode de trading:',
        'position_size_usdt': 'Taille de position (USDT):', 'leverage_label': 'Levier:',
        'market_interval_sec': 'Intervalle marché (s):', 'target_pnl': 'PNL cible (USDT):',
        'neutral_close_pct_label': 'Clôture neutre (%):', 'auto_balance_pct': 'Solde auto (%):',
        'stop_loss_pct_label': 'Stop Loss (%):', 'auto_on': 'Auto: Activé', 'auto_off': 'Auto: Désactivé',
        'account_info': 'Infos du compte', 'balance': 'Solde :', 'connection_status': 'Statut :', 'not_connected': 'Non connecté', 'connected_fmt': 'Connecté ✓ ({env})',
        'symbol_label': 'Symbole', 'selected_coin_info': 'Crypto sélectionnée', 'price': 'Prix :', 'change_24h': 'Variation (24h) :',
        'license_code': 'Code de licence :', 'license_status_unlicensed': 'Statut : Sans licence', 'license_status_active': 'Statut : Sous licence', 'license_status_invalid': 'Statut : Licence invalide', 'get_license': 'Acheter une licence', 'license_active_btn': 'Licence active',
        'update_available': 'Mise à jour disponible !',
        'help_position_size': 'USDT utilisé pour calculer la quantité.',
        'help_leverage': 'Levier appliqué avant l’ouverture de la position.',
        'help_market_interval': 'Fréquence de contrôle du marché (secondes).',
        'help_target_pnl': 'Ferme la position quand le PNL non réalisé atteint cette valeur.',
        'help_neutral_close_pct': 'Marché neutre: si |variation 24h| dépasse ce %, fermer.',
        'help_auto_balance_pct': 'Si >0, utilise ce % de votre USDT disponible par trade.',
        'help_stop_loss_pct': 'Si la perte atteint ce %, fermer la position.',
        'help_momentum_threshold': 'Si le nombre de pièces en hausse diminue de ce montant, fermez les positions et attendez le changement de tendance.',
        'user_guide_btn': 'Guide d\'Utilisation',
        'market_threshold_label': 'Seuil de Tendance du Marché',
        'momentum_threshold_label': 'Seuil de Perte de Momentum',
        'stop_loss_coin_label': 'Stop Loss:',
        'trade_percent_label': 'Commerce %:',
        'take_profit_pct_label': 'Prendre Profit (%):',
        'default_settings_btn': 'Paramètres par Défaut',
        'selected_coins_title': 'Pièces Sélectionnées',
        'crypto_news': 'Actualités Crypto',
        'open_positions_title': 'Positions Ouvertes',
        'selected_coin_info': 'Pièce Sélectionnée',
        'account_summary': 'Résumé du Compte',
        'multi_coin_selection': 'Sélection Multi-Pièces',
        'search_label': 'Rechercher:',
        'license_code': 'Code de Licence:',
        'user_guide_title': '📖 Guide d\'Utilisation - Bot de Trading Automatique de Futures Crypto',
        'user_guide_content': '''Bienvenue sur le Bot de Trading Automatique. Ce programme vous permet de trader automatiquement les contrats à terme de crypto-monnaies sur Binance en fonction de l\'analyse du marché et du momentum. Utilisez le mode TEST d\'abord, ne risquez que des fonds que vous pouvez vous permettre de perdre, comprenez les risques du levier. Utilisez uniquement les licences officielles de https://license.planc.space/'''
    },
    'ar': {
        'api': 'واجهة برمجة التطبيقات', 'sponsor': 'الراعي', 'license': 'الترخيص',
        'connect': 'اتصال', 'refresh_list': 'تحديث القائمة',
        'long': 'شراء', 'short': 'بيع', 'close_all': 'إغلاق الكل', 'close_selected': 'إغلاق المحدد',
        'auto_trade': 'تداول تلقائي', 'save_settings': 'حفظ الإعدادات', 'refresh': 'تحديث',
        'pnl_panel': 'PNL للصفقات المفتوحة', 'summary': 'الملخص', 'positions': 'الصفقات المفتوحة', 'history': 'السجل (المحقق)', 'log': 'السجل',
        'trading': 'التداول', 'trading_mode': 'وضع التداول:',
        'position_size_usdt': 'حجم الصفقة (USDT):', 'leverage_label': 'الرافعة:',
        'market_interval_sec': 'فاصل فحص السوق (ث):', 'target_pnl': 'الربح المستهدف (USDT):',
        'neutral_close_pct_label': 'إغلاق محايد (%):', 'auto_balance_pct': 'رصيد تلقائي (%):',
        'stop_loss_pct_label': 'إيقاف الخسارة (%):', 'auto_on': 'تلقائي: تشغيل', 'auto_off': 'تلقائي: إيقاف',
        'account_info': 'معلومات الحساب', 'balance': 'الرصيد:', 'connection_status': 'الحالة:', 'not_connected': 'غير متصل', 'connected_fmt': 'متصل ✓ ({env})',
        'symbol_label': 'الرمز', 'selected_coin_info': 'العملة المختارة', 'price': 'السعر:', 'change_24h': 'تغير (24س):',
        'license_code': 'رمز الترخيص:', 'license_status_unlicensed': 'الحالة: بدون ترخيص', 'license_status_active': 'الحالة: مرخص', 'license_status_invalid': 'الحالة: ترخيص غير صالح', 'get_license': 'شراء ترخيص', 'license_active_btn': 'ترخيص نشط',
        'update_available': 'تحديث متاح!',
        'help_position_size': 'قيمة USDT لحساب كمية الأمر.',
        'help_leverage': 'الرافعة المطبقة قبل فتح الصفقة.',
        'help_market_interval': 'عدد الثواني بين فحوصات السوق.',
        'help_target_pnl': 'إغلاق الصفقة عندما يصل الربح/الخسارة غير المحققة لهذه القيمة.',
        'help_neutral_close_pct': 'عند حياد السوق، إذا تجاوز تغير 24س هذا %، أغلق الصفقة.',
        'help_auto_balance_pct': 'إن كان >0 استخدم هذه النسبة من رصيد USDT المتاح.',
        'help_stop_loss_pct': 'إذا بلغت الخسارة هذه النسبة، أغلق الصفقة.',
        'help_momentum_threshold': 'إذا انخفض عدد العملات الصاعدة بهذا المقدار، أغلق المراكز وانتظر تغيير الاتجاه.',
        'user_guide_btn': 'دليل الاستخدام',
        'market_threshold_label': 'عتبة اتجاه السوق',
        'momentum_threshold_label': 'عتبة فقدان الزخم',
        'stop_loss_coin_label': 'Stop Loss:',
        'trade_percent_label': 'تداول %:',
        'take_profit_pct_label': 'أخذ الربح (%):',
        'default_settings_btn': 'الإعدادات الافتراضية',
        'selected_coins_title': 'العملات المختارة',
        'crypto_news': 'أخبار العملات المشفرة',
        'open_positions_title': 'الصفقات المفتوحة',
        'selected_coin_info': 'العملة المختارة',
        'account_summary': 'ملخص الحساب',
        'multi_coin_selection': 'اختيار عدة عملات',
        'search_label': 'البحث:',
        'license_code': 'رمز الترخيص:',
        'user_guide_title': '📖 دليل الاستخدام - بوت التداول التلقائي للعقود الآجلة للعملات المشفرة',
        'user_guide_content': '''مرحبًا بك في بوت التداول التلقائي. يتيح لك هذا البرنامج تداول العقود الآجلة للعملات المشفرة تلقائيًا على Binance بناءً على تحليل السوق والزخم. استخدم وضع TEST أولاً، خاطر فقط بالأموال التي يمكنك تحمل خسارتها، افهم مخاطر الرافعة المالية. استخدم فقط التراخيص الرسمية من https://license.planc.space/''',
        # Ek çeviriler
        'env_test': 'تجربة',
        'env_live': 'مباشر',
        'search_label': 'بحث:',
        'selected_count': 'المحدد: {count} عملة',
        'add_selected': 'إضافة المحدد',
        'remove_selected': 'إزالة المحدد',
        'multi_coin_selection': 'اختيار متعدد العملات',
        'market_neutral_text': 'السوق محايد',
        'market_rising_text': 'السوق في ارتفاع',
        'market_falling_text': 'السوق في انخفاض',
        'auto_trade_off_label': 'تداول تلقائي: إيقاف',
        'auto_trade_on_label': 'تداول تلقائي: تشغيل',
        'mode_test': 'الوضع: تجريبي',
        'mode_live': 'الوضع: مباشر',
        'selected_coins_title': 'العملات المختارة',
        'account_summary': 'ملخص الحساب',
        'open_positions_title': 'الصفقات المفتوحة',
        'close_all_trades': '[X] إغلاق كل الصفقات',
        'close_selected_trade': '[X] إغلاق المحدد',
        'auto_trade_btn': '>> تداول تلقائي',
        'save_settings_btn': '[S] حفظ الإعدادات',
        'refresh_btn': '[R] تحديث',
        'refresh_summary_btn': '[≡] تحديث الملخص',
        'update_btn': '[↓] تحديث',
        'api_keys_required': 'مفتاح API والسر مطلوبان!',
        'connect_api_first': 'يرجى الاتصال بـ API أولاً!',
        'positions_closed': 'تم إغلاق {count} صفقة!',
        'no_positions_to_close': 'لا توجد صفقات للإغلاق.',
        'select_position_from_table': 'يرجى تحديد صفقة من الجدول.',
        'trade_percent_label': 'نسبة التداول:',
        'rising_text': 'في ارتفاع',
        'falling_text': 'في انخفاض',
        'neutral_text': 'محايد',
        'settings_saved': 'تم حفظ الإعدادات.',
        'total_pnl_label': 'إجمالي PNL',
        'total_fee_label': 'إجمالي الرسوم',
        'total_trades_label': 'إجمالي الصفقات',
        'long_positions_label': 'صفقات الشراء',
        'short_positions_label': 'صفقات البيع',
        'total_balance_label': 'إجمالي الرصيد',
        'get_license_btn_text': 'شراء ترخيص',
        'connect_btn_text': 'اتصال',
        'language_label': 'اللغة / Language:',
        'api_connection_error': 'خطأ اتصال API: {error}',
        'disconnect': 'قطع الاتصال',
        # Position table headers
        'position_symbol': 'الرمز',
        'position_side': 'الاتجاه',
        'position_size': 'الحجم',
        'position_entry_price': 'سعر الدخول',
        'position_leverage': 'الرافعة',
        'position_pnl': 'الربح/الخسارة',
        'license_leverage_warning_title': 'الترخيص مطلوب',
        'license_leverage_warning_msg': '⚠️ الترخيص مطلوب!\n\n🔒 بدون ترخيص نشط، يُسمح فقط برافعة 1x.\n\n📦 احصل على ترخيص:\nhttps://license.planc.space/',
        'license_leverage_limited_log': '⚠️ لا يوجد ترخيص، الرافعة محدودة إلى 1x',
        'close_positions_warning_title': 'صفقات مفتوحة',
        'close_positions_warning_msg': '⚠️ لديك {count} صفقة مفتوحة!\n\nيرجى إغلاق صفقاتك يدويًا قبل الخروج من البرنامج.',
        'env_label': 'البيئة (تجربة/مباشر):',
        'error': 'خطأ',
        'success': 'نجح',
        'info': 'معلومات',
        'activate': 'تفعيل',
    },
    'zh': {
        'api': 'API', 'sponsor': '赞助', 'license': '许可证',
        'connect': '连接', 'refresh_list': '刷新列表', 'long': '多单', 'short': '空单',
        'close_all': '全部平仓', 'close_selected': '平所选', 'auto_trade': '自动交易', 'save_settings': '保存设置', 'refresh': '刷新',
        'pnl_panel': '未平仓PNL', 'summary': '汇总', 'positions': '持仓', 'history': '历史 (已实现)', 'log': '日志',
        'trading': '交易', 'trading_mode': '交易模式:', 'position_size_usdt': '仓位大小 (USDT):', 'leverage_label': '杠杆:',
        'market_interval_sec': '市场检查间隔(秒):', 'target_pnl': '目标PNL (USDT):', 'neutral_close_pct_label': '中性平仓 (%):',
        'auto_balance_pct': '自动资金比例 (%):', 'stop_loss_pct_label': '止损 (%):', 'auto_on': '自动: 开', 'auto_off': '自动: 关',
        'account_info': '账户信息', 'balance': '余额：', 'connection_status': '状态：', 'not_connected': '未连接', 'connected_fmt': '已连接 ✓ ({env})',
        'symbol_label': '交易对', 'selected_coin_info': '已选币种', 'price': '价格：', 'change_24h': '24小时变化：',
        'license_code': '许可证代码：', 'license_status_unlicensed': '状态：未授权', 'license_status_active': '状态：已授权', 'license_status_invalid': '状态：许可证无效', 'get_license': '购买许可证', 'license_active_btn': '许可证已激活',
        'update_available': '有可用更新！',
        'help_position_size': '用于计算下单数量的USDT金额。',
        'help_leverage': '开仓前设置的杠杆。',
        'help_market_interval': '市场监控的运行频率（秒）。',
        'help_target_pnl': '当未实现PNL达到此值时平仓。',
        'help_neutral_close_pct': '市场中性时，若24h涨跌幅超过该%，则平仓。',
        'help_auto_balance_pct': '若>0，每笔使用可用USDT的此百分比。',
        'help_stop_loss_pct': '亏损达到该%时自动平仓。',
        'help_momentum_threshold': '若上涨币种数量下降此数值，关闭持仓并等待趋势改变。',
        'user_guide_btn': '使用指南',
        'market_threshold_label': '市场趋势阈值',
        'momentum_threshold_label': '动量损失阈值',
        'stop_loss_coin_label': '止损:',
        'trade_percent_label': '交易 %:',
        'take_profit_pct_label': '获利 (%):',
        'default_settings_btn': '默认设置',
        'selected_coins_title': '选定的硬币',
        'crypto_news': '加密新闻',
        'open_positions_title': '开放头寸',
        'selected_coin_info': '选定的硬币',
        'account_summary': '账户摘要',
        'multi_coin_selection': '多硬币选择',
        'search_label': '搜索:',
        'license_code': '许可证代码:',
        'user_guide_title': '📖 使用指南 - 加密货币期货自动交易机器人',
        'user_guide_content': '''欢迎使用自动交易机器人。此程序允许您根据市场分析和动量在Binance上自动交易加密货币期货。首先使用测试模式，仅冒险可以承受损失的资金，了解杠杆风险。仅使用来自 https://license.planc.space/ 的官方许可证'''
    },
    'hi': {
        'api': 'API', 'sponsor': 'प्रायोजक', 'license': 'लाइसेंस',
        'connect': 'कनेक्ट', 'refresh_list': 'सूची रीफ़्रेश', 'long': 'लॉन्ग', 'short': 'शॉर्ट',
        'close_all': 'सब बंद करें', 'close_selected': 'चुना हुआ बंद', 'auto_trade': 'ऑटो ट्रेड', 'save_settings': 'सेटिंग्स सहेजें', 'refresh': 'रीफ़्रेश',
        'pnl_panel': 'खुली पोज़िशनों का PNL', 'summary': 'सारांश', 'positions': 'खुली पोज़िशन', 'history': 'इतिहास (रीलाइज़्ड)', 'log': 'लॉग',
        'trading': 'ट्रेडिंग', 'trading_mode': 'ट्रेडिंग मोड:', 'position_size_usdt': 'पोज़िशन साइज (USDT):', 'leverage_label': 'लिवरेज:',
        'market_interval_sec': 'मार्केट अंतराल (सेक.):', 'target_pnl': 'लक्ष्य PNL (USDT):', 'neutral_close_pct_label': 'न्यूट्रल क्लोज (%):',
        'auto_balance_pct': 'ऑटो बैलेंस (%):', 'stop_loss_pct_label': 'स्टॉप लॉस (%):', 'auto_on': 'ऑटो: चालू', 'auto_off': 'ऑटो: बंद',
        'account_info': 'खाता जानकारी', 'balance': 'बैलेंस:', 'connection_status': 'स्थिति:', 'not_connected': 'कनेक्ट नहीं', 'connected_fmt': 'कनेक्टेड ✓ ({env})',
        'symbol_label': 'सिंबल', 'selected_coin_info': 'चयनित कॉइन', 'price': 'कीमत:', 'change_24h': 'बदलाव (24h):',
        'license_code': 'लाइसेंस कोड:', 'license_status_unlicensed': 'स्थिति: बिना लाइसेंस', 'license_status_active': 'स्थिति: लाइसेंस सक्रिय', 'license_status_invalid': 'स्थिति: अमान्य लाइसेंस', 'get_license': 'लाइसेंस खरीदें', 'license_active_btn': 'लाइसेंस सक्रिय',
        'update_available': 'अपडेट उपलब्ध!',
        'help_position_size': 'ऑर्डर मात्रा निकालने के लिए USDT राशि।',
        'help_leverage': 'पोज़िशन खोलने से पहले लागू लिवरेज।',
        'help_market_interval': 'मार्केट चेक की आवृत्ति (सेकंड)।',
        'help_target_pnl': 'जब अनरियलाइज़्ड PNL इस मूल्य तक पहुंचे तो पोज़िशन बंद करें।',
        'help_neutral_close_pct': 'मार्केट न्यूट्रल होने पर 24h परिवर्तन |%| इस मान से अधिक हो तो बंद करें।',
        'help_auto_balance_pct': 'यदि >0, प्रति ट्रेड उपलब्ध USDT का यह % उपयोग करें।',
        'help_stop_loss_pct': 'हानि इस % तक पहुँचने पर पोज़िशन बंद करें।',
        'help_momentum_threshold': 'यदि बढ़ते हुए कॉइनों की संख्या इस मात्रा से घट जाए, तो पोज़िशन बंद करें और ट्रेंड बदलाव का इंतज़ार करें।',
        'user_guide_btn': 'उपयोग गाइड',
        'market_threshold_label': 'बाजार प्रवृत्ति थ्रेशोल्ड',
        'momentum_threshold_label': 'संवेग हानि थ्रेशोल्ड',
        'stop_loss_coin_label': 'स्टॉप लॉस:',
        'trade_percent_label': 'ट्रेड %:',
        'take_profit_pct_label': 'लाभ लेना (%):',
        'default_settings_btn': 'डिफ़ॉल्ट सेटिंग्स',
        'selected_coins_title': 'चयनित सिक्के',
        'crypto_news': 'क्रिप्टो समाचार',
        'open_positions_title': 'खुले पद',
        'selected_coin_info': 'चयनित सिक्का',
        'account_summary': 'खाता सारांश',
        'multi_coin_selection': 'कई सिक्का चयन',
        'search_label': 'खोजें:',
        'license_code': 'लाइसेंस कोड:',
        'user_guide_title': '📖 उपयोग गाइड - क्रिप्टो फ्यूचर्स ऑटो ट्रेडिंग बॉट',
        'user_guide_content': '''ऑटो ट्रेडिंग बॉट में आपका स्वागत है। यह प्रोग्राम आपको बाज़ार विश्लेषण और मोमेंटम के आधार पर Binance पर स्वचालित रूप से क्रिप्टोकरेंसी फ्यूचर्स ट्रेड करने की अनुमति देता है। पहले TEST मोड का उपयोग करें, केवल उन फंड को जोखिम में डालें जिन्हें आप खो सकते हैं, लीवरेज जोखिमों को समझें। केवल https://license.planc.space/ से आधिकारिक लाइसेंस का उपयोग करें'''
    },
    'pt': {
        'api': 'API', 'sponsor': 'Patrocinador', 'license': 'Licença',
        'connect': 'Conectar', 'refresh_list': 'Atualizar lista', 'long': 'LONG', 'short': 'SHORT',
        'close_all': 'Fechar tudo', 'close_selected': 'Fechar selecionado', 'auto_trade': 'Trade automático', 'save_settings': 'Salvar', 'refresh': 'Atualizar',
        'pnl_panel': 'PNL das operações abertas', 'summary': 'Resumo', 'positions': 'Posições abertas', 'history': 'Histórico (Realizado)', 'log': 'Log',
        'trading': 'Trading', 'trading_mode': 'Modo de trading:', 'position_size_usdt': 'Tamanho da posição (USDT):', 'leverage_label': 'Alavancagem:',
        'market_interval_sec': 'Intervalo de verificação (s):', 'target_pnl': 'PNL alvo (USDT):', 'neutral_close_pct_label': 'Fechamento neutro (%):',
        'auto_balance_pct': 'Saldo automático (%):', 'stop_loss_pct_label': 'Stop Loss (%):', 'auto_on': 'Auto: Ligado', 'auto_off': 'Auto: Desligado',
        'account_info': 'Informações da conta', 'balance': 'Saldo:', 'connection_status': 'Status:', 'not_connected': 'Desconectado', 'connected_fmt': 'Conectado ✓ ({env})',
        'symbol_label': 'Símbolo', 'selected_coin_info': 'Moeda selecionada', 'price': 'Preço:', 'change_24h': 'Variação (24h):',
        'license_code': 'Código da licença:', 'license_status_unlicensed': 'Status: Sem licença', 'license_status_active': 'Status: Licenciado', 'license_status_invalid': 'Status: Licença inválida', 'get_license': 'Comprar licença', 'license_active_btn': 'Licença ativa',
        'update_available': 'Atualização disponível!',
        'help_position_size': 'USDT usado para calcular a quantidade.',
        'help_leverage': 'Alavancagem a aplicar antes de abrir posição.',
        'help_market_interval': 'Frequência do monitor de mercado (segundos).',
        'help_target_pnl': 'Fecha a posição quando o PNL não realizado atingir este valor.',
        'help_neutral_close_pct': 'Com mercado neutro, se |variação 24h| exceder este %, fechar.',
        'help_auto_balance_pct': 'Se >0, usa este % do seu USDT disponível por trade.',
        'help_stop_loss_pct': 'Se a perda atingir este %, fechar a posição.',
        'help_momentum_threshold': 'Se o número de moedas em alta cair nesta quantidade, feche posições e aguarde mudança de tendência.',
        'user_guide_btn': 'Guia de Uso',
        'market_threshold_label': 'Limiar de Tendência do Mercado',
        'momentum_threshold_label': 'Limiar de Perda de Momentum',
        'stop_loss_coin_label': 'Stop Loss:',
        'trade_percent_label': 'Negociação %:',
        'take_profit_pct_label': 'Tomar Lucro (%):',
        'default_settings_btn': 'Configurações Padrão',
        'selected_coins_title': 'Moedas Selecionadas',
        'crypto_news': 'Notícias de Cripto',
        'open_positions_title': 'Posições Abertas',
        'selected_coin_info': 'Moeda Selecionada',
        'account_summary': 'Resumo da Conta',
        'multi_coin_selection': 'Seleção de Múltiplas Moedas',
        'search_label': 'Buscar:',
        'license_code': 'Código de Licença:',
        'user_guide_title': '📖 Guia de Uso - Bot de Trading Automático de Futuros Cripto',
        'user_guide_content': '''Bem-vindo ao Bot de Trading Automático. Este programa permite negociar automaticamente futuros de criptomoedas na Binance com base em análise de mercado e momentum. Use o modo TEST primeiro, arrisque apenas fundos que você pode perder, entenda os riscos de alavancagem. Use apenas licenças oficiais de https://license.planc.space/''',
        'env_test': 'Teste',
        'env_live': 'Real',
        'search_label': 'Buscar:',
        'selected_count': 'Selecionado: {count} moedas',
        'add_selected': 'Adicionar selecionado',
        'remove_selected': 'Remover selecionado',
        'multi_coin_selection': 'Seleção múltipla de moedas',
        'market_neutral_text': 'Mercado neutro',
        'market_rising_text': 'Mercado em alta',
        'market_falling_text': 'Mercado em baixa',
        'auto_trade_off_label': 'Trade automático: Desligado',
        'auto_trade_on_label': 'Trade automático: Ligado',
        'mode_test': 'Modo: Teste',
        'mode_live': 'Modo: Real',
        'selected_coins_title': 'Moedas selecionadas',
        'account_summary': 'Resumo da conta',
        'open_positions_title': 'Posições abertas',
        'close_all_trades': '[X] Fechar tudo',
        'close_selected_trade': '[X] Fechar selecionado',
        'auto_trade_btn': '>> Trade automático',
        'save_settings_btn': '[S] Salvar',
        'refresh_btn': '[R] Atualizar',
        'refresh_summary_btn': '[≡] Atualizar resumo',
        'update_btn': '[↓] Atualizar',
        'total_pnl_label': 'PNL total',
        'total_fee_label': 'Taxas totais',
        'total_trades_label': 'Total de operações',
        'long_positions_label': 'Posições LONG',
        'short_positions_label': 'Posições SHORT',
        'total_balance_label': 'Saldo total',
        'get_license_btn_text': 'Comprar licença',
        'connect_btn_text': 'Conectar',
        'language_label': 'Idioma / Language:',
        'api_connection_error': 'Erro de conexão API: {error}',
        'disconnect': 'Desconectar',
        'position_symbol': 'Símbolo',
        'position_side': 'Lado',
        'position_size': 'Tamanho',
        'position_entry_price': 'Preço de entrada',
        'position_leverage': 'Alavancagem',
        'position_pnl': 'PNL',
        'license_leverage_warning_title': 'Licença Necessária',
        'license_leverage_warning_msg': '⚠️ Licença Necessária!\n\n🔒 Sem uma licença ativa, apenas alavancagem 1x é permitida.\n\n📦 Obter licença:\nhttps://license.planc.space/',
        'license_leverage_limited_log': '⚠️ Sem licença, alavancagem limitada a 1x',
        'close_positions_warning_title': 'Posições Abertas',
        'close_positions_warning_msg': '⚠️ Você tem {count} posição(ões) aberta(s)!\n\nPor favor, feche suas posições manualmente antes de sair do programa.',
        'rising_text': 'Em alta',
        'falling_text': 'Em baixa',
        'neutral_text': 'Neutro',
        'settings_saved': 'Configurações salvas.',
        'api_keys_required': 'Chave e segredo da API são obrigatórios!',
        'connect_api_first': 'Conecte-se à API primeiro!',
        'positions_closed': '{count} posições fechadas!',
        'no_positions_to_close': 'Nenhuma posição para fechar.',
        'select_position_from_table': 'Selecione uma posição da tabela.',
        'env_label': 'Ambiente (Teste/Real):',
        'api_key': 'Chave API:',
        'api_secret': 'Segredo API:',
        'error': 'Erro',
        'success': 'Sucesso',
        'info': 'Informação',
        'activate': 'Ativar',
    },
    'ru': {
        'api': 'API', 'sponsor': 'Спонсор', 'license': 'Лицензия',
        'connect': 'Подключить', 'refresh_list': 'Обновить список', 'long': 'Лонг', 'short': 'Шорт',
        'close_all': 'Закрыть все', 'close_selected': 'Закрыть выбранное', 'auto_trade': 'Автоторговля', 'save_settings': 'Сохранить', 'refresh': 'Обновить',
        'pnl_panel': 'PNL открытых позиций', 'summary': 'Сводка', 'positions': 'Открытые позиции', 'history': 'История (Реализ.)', 'log': 'Лог',
        'trading': 'Торговля', 'trading_mode': 'Режим торговли:', 'position_size_usdt': 'Размер позиции (USDT):', 'leverage_label': 'Плечо:',
        'market_interval_sec': 'Интервал проверки (с):', 'target_pnl': 'Целевой PNL (USDT):', 'neutral_close_pct_label': 'Нейтральное закрытие (%):',
        'auto_balance_pct': 'Авто баланс (%):', 'stop_loss_pct_label': 'Стоп-лосс (%):', 'auto_on': 'Авто: Вкл', 'auto_off': 'Авто: Выкл',
        'account_info': 'Информация аккаунта', 'balance': 'Баланс:', 'connection_status': 'Статус:', 'not_connected': 'Не подключено', 'connected_fmt': 'Подключено ✓ ({env})',
        'symbol_label': 'Символ', 'selected_coin_info': 'Выбранная монета', 'price': 'Цена:', 'change_24h': 'Изменение (24ч):',
        'license_code': 'Код лицензии:', 'license_status_unlicensed': 'Статус: без лицензии', 'license_status_active': 'Статус: лицензировано', 'license_status_invalid': 'Статус: неверная лицензия', 'get_license': 'Купить лицензию', 'license_active_btn': 'Лицензия активна',
        'update_available': 'Доступно обновление!',
        'help_position_size': 'Сумма USDT для расчёта количества ордера.',
        'help_leverage': 'Плечо, устанавливаемое перед открытием позиции.',
        'help_market_interval': 'Период работы монитора рынка (сек).',
        'help_target_pnl': 'Закрыть позицию, когда нереализ. PNL достигнет значения.',
        'help_neutral_close_pct': 'При нейтральном рынке, если |24ч изменение| > %, закрыть.',
        'help_auto_balance_pct': 'Если >0, использовать этот % доступного USDT на сделку.',
        'help_stop_loss_pct': 'Если убыток достигнет этого %, закрыть позицию.',
        'help_momentum_threshold': 'Если количество растущих монет упадёт на это значение, закройте позиции и ждите изменения тренда.',
        'user_guide_btn': 'Руководство',
        'market_threshold_label': 'Порог Тренда Рынка',
        'momentum_threshold_label': 'Порог Потери Импульса',
        'stop_loss_coin_label': 'Стоп-лосс:',
        'trade_percent_label': 'Торговля %:',
        'take_profit_pct_label': 'Взять Прибыль (%):',
        'default_settings_btn': 'Настройки по Умолчанию',
        'selected_coins_title': 'Выбранные Монеты',
        'crypto_news': 'Крипто Новости',
        'open_positions_title': 'Открытые Позиции',
        'selected_coin_info': 'Выбранная Монета',
        'account_summary': 'Сводка Аккаунта',
        'multi_coin_selection': 'Выбор Нескольких Монет',
        'search_label': 'Поиск:',
        'license_code': 'Код Лицензии:',
        'user_guide_title': '📖 Руководство - Бот Автоматической Торговли Крипто-Фьючерсами',
        'user_guide_content': '''Добро пожаловать в Бот Автоматической Торговли. Эта программа позволяет автоматически торговать криптовалютными фьючерсами на Binance на основе анализа рынка и импульса. Сначала используйте ТЕСТОВЫЙ режим, рискуйте только теми средствами, которые можете потерять, понимайте риски кредитного плеча. Используйте только официальные лицензии с https://license.planc.space/''',
        'env_test': 'Тест',
        'env_live': 'Реал',
        'search_label': 'Поиск:',
        'selected_count': 'Выбрано: {count} монет',
        'add_selected': 'Добавить выбранное',
        'remove_selected': 'Удалить выбранное',
        'multi_coin_selection': 'Выбор нескольких монет',
        'market_neutral_text': 'Рынок нейтрален',
        'market_rising_text': 'Рынок растёт',
        'market_falling_text': 'Рынок падает',
        'auto_trade_off_label': 'Автоторговля: Выкл',
        'auto_trade_on_label': 'Автоторговля: Вкл',
        'mode_test': 'Режим: Тест',
        'mode_live': 'Режим: Реал',
        'selected_coins_title': 'Выбранные монеты',
        'account_summary': 'Сводка аккаунта',
        'open_positions_title': 'Открытые позиции',
        'close_all_trades': '[X] Закрыть все',
        'close_selected_trade': '[X] Закрыть выбранное',
        'auto_trade_btn': '>> Автоторговля',
        'save_settings_btn': '[S] Сохранить',
        'refresh_btn': '[R] Обновить',
        'refresh_summary_btn': '[≡] Обновить сводку',
        'update_btn': '[↓] Обновление',
        'total_pnl_label': 'Общий PNL',
        'total_fee_label': 'Общие комиссии',
        'total_trades_label': 'Всего сделок',
        'long_positions_label': 'Лонг позиции',
        'short_positions_label': 'Шорт позиции',
        'total_balance_label': 'Общий баланс',
        'get_license_btn_text': 'Купить лицензию',
        'connect_btn_text': 'Подключить',
        'language_label': 'Язык / Language:',
        'api_connection_error': 'Ошибка подключения API: {error}',
        'disconnect': 'Отключить',
        'position_symbol': 'Символ',
        'position_side': 'Сторона',
        'position_size': 'Размер',
        'position_entry_price': 'Цена входа',
        'position_leverage': 'Плечо',
        'position_pnl': 'PNL',
        'license_leverage_warning_title': 'Требуется Лицензия',
        'license_leverage_warning_msg': '⚠️ Требуется Лицензия!\n\n🔒 Без активной лицензии разрешено только плечо 1x.\n\n📦 Получить лицензию:\nhttps://license.planc.space/',
        'license_leverage_limited_log': '⚠️ Нет лицензии, плечо ограничено до 1x',
        'close_positions_warning_title': 'Открытые Позиции',
        'close_positions_warning_msg': '⚠️ У вас есть {count} открытая(ых) позиция(й)!\n\nПожалуйста, закройте ваши позиции вручную перед выходом из программы.',
        'rising_text': 'Растёт',
        'falling_text': 'Падает',
        'neutral_text': 'Нейтрален',
        'settings_saved': 'Настройки сохранены.',
        'api_keys_required': 'Требуются API ключ и секрет!',
        'connect_api_first': 'Сначала подключитесь к API!',
        'positions_closed': 'Закрыто {count} позиций!',
        'no_positions_to_close': 'Нет позиций для закрытия.',
        'select_position_from_table': 'Выберите позицию из таблицы.',
        'env_label': 'Среда (Тест/Реал):',
        'api_key': 'API Ключ:',
        'api_secret': 'API Секрет:',
        'error': 'Ошибка',
        'success': 'Успех',
        'info': 'Информация',
        'activate': 'Активировать',
        'license_status_active_short': 'Активна',
        'balance_percent_label': 'Автобаланс (%):',
        'market_threshold_label': 'Порог Тренда Рынка',
        'momentum_threshold_label': 'Порог Потери Импульса',
        'stop_loss_coin_label': 'Стоп-лосс:',
        'take_profit_pct_label': 'Взять Прибыль (%):',
    },
    'bn': {
        'api': 'API', 'sponsor': 'স্পনসর', 'license': 'লাইসেন্স',
        'connect': 'কানেক্ট', 'refresh_list': 'তালিকা রিফ্রেশ', 'long': 'লং', 'short': 'শর্ট',
        'close_all': 'সব বন্ধ করুন', 'close_selected': 'নির্বাচিত বন্ধ', 'auto_trade': 'অটো ট্রেড', 'save_settings': 'সেভ', 'refresh': 'রিফ্রেশ',
        'pnl_panel': 'ওপেন ট্রেড PNL', 'summary': 'সারসংক্ষেপ', 'positions': 'ওপেন পজিশন', 'history': 'ইতিহাস (রিয়েলাইজড)', 'log': 'লগ',
        'trading': 'ট্রেডিং', 'trading_mode': 'ট্রেডিং মোড:', 'position_size_usdt': 'পজিশন সাইজ (USDT):', 'leverage_label': 'লিভারেজ:',
        'market_interval_sec': 'বাজার অন্তর (সেকেন্ড):', 'target_pnl': 'টার্গেট PNL (USDT):', 'neutral_close_pct_label': 'নিরপেক্ষ ক্লোজ (%):',
        'auto_balance_pct': 'অটো ব্যালেন্স (%):', 'stop_loss_pct_label': 'স্টপ লস (%):', 'auto_on': 'অটো: অন', 'auto_off': 'অটো: অফ',
        'account_info': 'অ্যাকাউন্ট তথ্য', 'balance': 'ব্যালেন্স:', 'connection_status': 'স্ট্যাটাস:', 'not_connected': 'সংযুক্ত নয়', 'connected_fmt': 'সংযুক্ত ✓ ({env})',
        'symbol_label': 'সিম্বল', 'selected_coin_info': 'নির্বাচিত কয়েন', 'price': 'দাম:', 'change_24h': 'পরিবর্তন (24ঘ):',
        'license_code': 'লাইসেন্স কোড:', 'license_status_unlicensed': 'স্ট্যাটাস: লাইসেন্স নেই', 'license_status_active': 'স্ট্যাটাস: লাইসেন্স সক্রিয়', 'license_status_invalid': 'স্ট্যাটাস: অবৈধ লাইসেন্স', 'get_license': 'লাইসেন্স কিনুন', 'license_active_btn': 'লাইসেন্স অ্যাক্টিভ',
        'update_available': 'আপডেট উপলভ্য!',
        'help_position_size': 'অর্ডার পরিমাণ গণনায় ব্যবহৃত USDT।',
        'help_leverage': 'পজিশন খোলার আগে প্রয়োগ করা লিভারেজ।',
        'help_market_interval': 'বাজার পরীক্ষা সময় (সেকেন্ড)।',
        'help_target_pnl': 'অনরিয়ালাইজড PNL এই মানে পৌঁছালে পজিশন বন্ধ করুন।',
        'help_neutral_close_pct': 'বাজার নিরপেক্ষ হলে 24ঘ পরিবর্তন |%| বেশি হলে বন্ধ করুন।',
        'help_auto_balance_pct': 'যদি >0 হয়, প্রতি ট্রেডে এই % USDT ব্যবহার করুন।',
        'help_stop_loss_pct': 'ক্ষতি এই % হলে পজিশন বন্ধ করুন।',
        'help_momentum_threshold': 'যদি বাড়তি কয়েনের সংখ্যা এই পরিমাণে কমে যায়, পজিশন বন্ধ করুন এবং ট্রেন্ড পরিবর্তনের জন্য অপেক্ষা করুন।',
        'user_guide_btn': 'ব্যবহার গাইড',
        'market_threshold_label': 'বাজার প্রবণতা থ্রেশহোল্ড',
        'momentum_threshold_label': 'মোমেন্টাম ক্ষতি থ্রেশহোল্ড',
        'stop_loss_coin_label': 'স্টপ লস:',
        'trade_percent_label': 'ট্রেড %:',
        'take_profit_pct_label': 'লাভ নিন (%):',
        'default_settings_btn': 'ডিফল্ট সেটিংস',
        'selected_coins_title': 'নির্বাচিত কয়েন',
        'crypto_news': 'ক্রিপ্টো সংবাদ',
        'open_positions_title': 'খোলা পজিশন',
        'selected_coin_info': 'নির্বাচিত কয়েন',
        'account_summary': 'অ্যাকাউন্ট সারাংশ',
        'multi_coin_selection': 'একাধিক কয়েন নির্বাচন',
        'search_label': 'খোঁজা:',
        'license_code': 'লাইসেন্স কোড:',
        'user_guide_title': '📖 ব্যবহার গাইড - ক্রিপ্টো ফিউচার অটো ট্রেডিং বট',
        'user_guide_content': '''অটো ট্রেডিং বটে স্বাগতম। এই প্রোগ্রামটি বাজার বিশ্লেষণ এবং মোমেন্টামের উপর ভিত্তি করে Binance-এ স্বয়ংক্রিয়ভাবে ক্রিপ্টোকারেন্সি ফিউচার ট্রেড করতে দেয়। প্রথমে TEST মোড ব্যবহার করুন, শুধুমাত্র যে তহবিল হারাতে পারেন তা দিয়ে ঝুঁকি নিন, লিভারেজ ঝুঁকি বুঝুন। শুধুমাত্র https://license.planc.space/ থেকে অফিসিয়াল লাইসেন্স ব্যবহার করুন'''
    },
    'ur': {
        'api': 'API', 'sponsor': 'اسپانسر', 'license': 'لائسنس',
        'connect': 'کنیکٹ', 'refresh_list': 'فہرست تازہ کریں', 'long': 'لانگ', 'short': 'شارٹ',
        'close_all': 'سب بند کریں', 'close_selected': 'منتخب بند کریں', 'auto_trade': 'آٹو ٹریڈ', 'save_settings': 'سیٹنگز محفوظ کریں', 'refresh': 'ریفریش',
        'pnl_panel': 'اوپن ٹریڈز PNL', 'summary': 'خلاصہ', 'positions': 'کھلی پوزیشنز', 'history': 'تاریخچہ (حقیقی)', 'log': 'لاگ',
        'trading': 'ٹریڈنگ', 'trading_mode': 'ٹریڈنگ موڈ:', 'position_size_usdt': 'پوزیشن سائز (USDT):', 'leverage_label': 'لیوریج:',
        'market_interval_sec': 'مارکیٹ وقفہ (سیکنڈ):', 'target_pnl': 'ہدف PNL (USDT):', 'neutral_close_pct_label': 'نیوٹرل کلوز (%):',
        'auto_balance_pct': 'آٹو بیلنس (%):', 'stop_loss_pct_label': 'اسٹاپ لاس (%):', 'auto_on': 'آٹو: آن', 'auto_off': 'آٹو: آف',
        'account_info': 'اکاؤنٹ معلومات', 'balance': 'بیلنس:', 'connection_status': 'حالت:', 'not_connected': 'منسلک نہیں', 'connected_fmt': 'منسلک ✓ ({env})',
        'symbol_label': 'سمبل', 'selected_coin_info': 'منتخب کوائن', 'price': 'قیمت:', 'change_24h': 'تبدیلی (24گھ):',
        'license_code': 'لائسنس کوڈ:', 'license_status_unlicensed': 'حالت: بغیر لائسنس', 'license_status_active': 'حالت: لائسنس یافتہ', 'license_status_invalid': 'حالت: غلط لائسنس', 'get_license': 'لائسنس خریدیں', 'license_active_btn': 'لائسنس فعال',
        'update_available': 'اپڈیٹ دستیاب!',
        'help_position_size': 'آرڈر مقدار نکالنے کے لیے USDT رقم۔',
        'help_leverage': 'پوزیشن کھولنے سے پہلے لگایا جانے والا لیوریج۔',
        'help_market_interval': 'مارکیٹ چیک کرنے کا وقفہ (سیکنڈ).',
        'help_target_pnl': 'جب غیر محسوس PNL اس قدر تک پہنچے تو پوزیشن بند کریں۔',
        'help_neutral_close_pct': 'مارکیٹ نیوٹرل ہو تو اگر 24گھنٹے تبدیلی اس فیصد سے بڑھے تو بند کریں۔',
        'help_auto_balance_pct': 'اگر >0 ہو، ہر ٹریڈ میں دستیاب USDT کا یہ % استعمال کریں۔',
        'help_stop_loss_pct': 'نقصان اس % پر پہنچتے ہی پوزیشن بند کریں۔',
        'help_momentum_threshold': 'اگر بڑھتے ہوئے سکوں کی تعداد اس مقدار سے کم ہو جائے تو پوزیشنیں بند کریں اور رجحان تبدیلی کا انتظار کریں۔',
        'user_guide_btn': 'استعمال گائیڈ',
        'market_threshold_label': 'مارکیٹ ٹرینڈ دہلیز',
        'momentum_threshold_label': 'موومنٹم نقصان دہلیز',
        'stop_loss_coin_label': 'سٹاپ لاس:',
        'trade_percent_label': 'ٹریڈ %:',
        'take_profit_pct_label': 'فائدہ اٹھائیں (%):',
        'default_settings_btn': 'ڈیفالٹ ترتیبات',
        'selected_coins_title': 'منتخب سکے',
        'crypto_news': 'کرپٹو نیوز',
        'open_positions_title': 'کھلی پوزیشنیں',
        'selected_coin_info': 'منتخب سکہ',
        'account_summary': 'اکاؤنٹ خلاصہ',
        'multi_coin_selection': 'کئی سکے منتخب کریں',
        'search_label': 'تلاش:',
        'license_code': 'لائسنس کوڈ:',
        'user_guide_title': '📖 استعمال گائیڈ - کریپٹو فیوچرز آٹو ٹریڈنگ بوٹ',
        'user_guide_content': '''آٹو ٹریڈنگ بوٹ میں خوش آمدید۔ یہ پروگرام مارکیٹ کے تجزیے اور رفتار کی بنیاد پر Binance پر خودکار طور پر کریپٹوکرنسی فیوچرز ٹریڈ کرنے کی اجازت دیتا ہے۔ پہلے TEST موڈ استعمال کریں، صرف وہ فنڈز خطرے میں ڈالیں جو آپ کھو سکتے ہیں، لیوریج کے خطرات کو سمجھیں۔ صرف https://license.planc.space/ سے سرکاری لائسنس استعمال کریں'''
    }
}


# Ensure all listed languages have at least English texts as fallback packs
for code, _ in LANGS:
    if code not in TRANSLATIONS:
        TRANSLATIONS[code] = TRANSLATIONS.get('en', {})


def get_text(lang: str, key: str) -> str:
    try:
        # Normalize: accept values like "en - English"
        if ' - ' in lang:
            lang = lang.split(' - ')[0]
    except Exception:
        pass
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]
    # fallback to English
    return TRANSLATIONS.get('en', {}).get(key, key)
