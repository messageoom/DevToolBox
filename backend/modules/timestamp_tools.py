from flask import Blueprint, request, jsonify
import time
import datetime

timestamp_tools_bp = Blueprint('timestamp_tools', __name__)

@timestamp_tools_bp.route('/current', methods=['GET'])
def get_current_timestamp():
    """获取当前时间戳"""
    try:
        current_time = time.time()
        utc_time = datetime.datetime.utcnow()

        # 获取当前时区
        import pytz
        local_tz = pytz.timezone('Asia/Shanghai')  # 默认时区
        try:
            # 尝试获取系统时区
            import tzlocal
            local_tz = tzlocal.get_localzone()
        except ImportError:
            pass

        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)

        # 常用时区列表
        timezones = {
            'local': {
                'name': '本地时间',
                'timezone': str(local_tz),
                'datetime': local_time.strftime('%Y-%m-%d %H:%M:%S'),
                'offset': local_time.strftime('%z')
            },
            'utc': {
                'name': 'UTC',
                'timezone': 'UTC',
                'datetime': utc_time.strftime('%Y-%m-%d %H:%M:%S'),
                'offset': '+0000'
            },
            'est': {
                'name': '美国东部时间',
                'timezone': 'US/Eastern',
                'datetime': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'),
                'offset': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Eastern')).strftime('%z')
            },
            'pst': {
                'name': '美国太平洋时间',
                'timezone': 'US/Pacific',
                'datetime': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S'),
                'offset': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Pacific')).strftime('%z')
            },
            'gmt': {
                'name': '格林威治时间',
                'timezone': 'GMT',
                'datetime': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('GMT')).strftime('%Y-%m-%d %H:%M:%S'),
                'offset': '+0000'
            },
            'cet': {
                'name': '欧洲中部时间',
                'timezone': 'Europe/Berlin',
                'datetime': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S'),
                'offset': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Berlin')).strftime('%z')
            },
            'jst': {
                'name': '日本标准时间',
                'timezone': 'Asia/Tokyo',
                'datetime': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S'),
                'offset': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Tokyo')).strftime('%z')
            },
            'cst': {
                'name': '中国标准时间',
                'timezone': 'Asia/Shanghai',
                'datetime': utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'),
                'offset': '+0800'
            }
        }

        return jsonify({
            'success': True,
            'timestamp': int(current_time),
            'timestamp_ms': int(current_time * 1000),
            'datetime': datetime.datetime.fromtimestamp(current_time).isoformat(),
            'local_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timezones': timezones,
            'current_timezone': str(local_tz)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timestamp_tools_bp.route('/convert', methods=['POST'])
def convert_timestamp():
    """转换时间戳"""
    try:
        data = request.get_json()
        if not data or 'timestamp' not in data:
            return jsonify({'error': '请提供timestamp字段'}), 400

        timestamp = data['timestamp']
        timestamp_type = data.get('type', 'seconds')  # seconds 或 milliseconds

        try:
            if timestamp_type == 'milliseconds':
                timestamp_seconds = timestamp / 1000
            else:
                timestamp_seconds = timestamp

            dt = datetime.datetime.fromtimestamp(timestamp_seconds)

            # 获取北京时间
            import pytz
            beijing_tz = pytz.timezone('Asia/Shanghai')
            beijing_time = dt.replace(tzinfo=pytz.utc).astimezone(beijing_tz)

            return jsonify({
                'success': True,
                'timestamp': int(timestamp_seconds),
                'timestamp_ms': int(timestamp_seconds * 1000),
                'datetime': dt.isoformat(),
                'formatted': {
                    'iso': dt.isoformat(),
                    'local': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'utc': dt.astimezone(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ'),
                    'beijing': beijing_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'date': dt.strftime('%Y-%m-%d'),
                    'time': dt.strftime('%H:%M:%S')
                }
            }), 200

        except (ValueError, OSError) as e:
            return jsonify({'error': f'时间戳格式错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timestamp_tools_bp.route('/parse', methods=['POST'])
def parse_datetime():
    """解析日期时间字符串"""
    try:
        data = request.get_json()
        if not data or 'datetime_string' not in data:
            return jsonify({'error': '请提供datetime_string字段'}), 400

        datetime_string = data['datetime_string']
        format_string = data.get('format', '%Y-%m-%d %H:%M:%S')

        try:
            dt = datetime.datetime.strptime(datetime_string, format_string)
            timestamp = int(dt.timestamp())

            return jsonify({
                'success': True,
                'timestamp': timestamp,
                'timestamp_ms': timestamp * 1000,
                'datetime': dt.isoformat(),
                'parsed': {
                    'year': dt.year,
                    'month': dt.month,
                    'day': dt.day,
                    'hour': dt.hour,
                    'minute': dt.minute,
                    'second': dt.second,
                    'weekday': dt.weekday(),
                    'isoweekday': dt.isoweekday()
                }
            }), 200

        except ValueError as e:
            return jsonify({'error': f'日期时间格式错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timestamp_tools_bp.route('/calculate', methods=['POST'])
def calculate_time():
    """时间计算"""
    try:
        data = request.get_json()
        if not data or 'base_timestamp' not in data:
            return jsonify({'error': '请提供base_timestamp字段'}), 400

        base_timestamp = data['base_timestamp']
        operation = data.get('operation', 'add')  # add 或 subtract
        unit = data.get('unit', 'seconds')  # seconds, minutes, hours, days
        amount = data.get('amount', 1)

        try:
            base_dt = datetime.datetime.fromtimestamp(base_timestamp)

            # 计算时间差
            if unit == 'seconds':
                delta = datetime.timedelta(seconds=amount)
            elif unit == 'minutes':
                delta = datetime.timedelta(minutes=amount)
            elif unit == 'hours':
                delta = datetime.timedelta(hours=amount)
            elif unit == 'days':
                delta = datetime.timedelta(days=amount)
            else:
                return jsonify({'error': '不支持的时间单位'}), 400

            if operation == 'add':
                result_dt = base_dt + delta
            elif operation == 'subtract':
                result_dt = base_dt - delta
            else:
                return jsonify({'error': '不支持的操作类型'}), 400

            result_timestamp = int(result_dt.timestamp())

            return jsonify({
                'success': True,
                'original_timestamp': base_timestamp,
                'original_datetime': base_dt.isoformat(),
                'result_timestamp': result_timestamp,
                'result_datetime': result_dt.isoformat(),
                'difference_seconds': result_timestamp - base_timestamp,
                'operation': f'{operation} {amount} {unit}'
            }), 200

        except (ValueError, OSError) as e:
            return jsonify({'error': f'时间戳格式错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timestamp_tools_bp.route('/difference', methods=['POST'])
def calculate_time_difference():
    """计算两个时间之间的差值"""
    try:
        data = request.get_json()
        if not data or 'start_time' not in data or 'end_time' not in data:
            return jsonify({'error': '请提供start_time和end_time字段'}), 400

        start_time = data['start_time']
        end_time = data['end_time']
        time_type = data.get('type', 'timestamp')  # timestamp 或 datetime_string

        try:
            if time_type == 'datetime_string':
                format_string = data.get('format', '%Y-%m-%d %H:%M:%S')
                start_dt = datetime.datetime.strptime(start_time, format_string)
                end_dt = datetime.datetime.strptime(end_time, format_string)
            else:
                start_dt = datetime.datetime.fromtimestamp(start_time)
                end_dt = datetime.datetime.fromtimestamp(end_time)

            # 计算时间差
            time_diff = end_dt - start_dt

            # 分解时间差
            total_seconds = int(time_diff.total_seconds())
            days = time_diff.days
            hours, remainder = divmod(abs(total_seconds), 3600)
            minutes, seconds = divmod(remainder, 60)

            return jsonify({
                'success': True,
                'start_time': start_time,
                'end_time': end_time,
                'difference': {
                    'total_seconds': total_seconds,
                    'days': days,
                    'hours': hours,
                    'minutes': minutes,
                    'seconds': seconds,
                    'human_readable': _format_time_difference(time_diff)
                },
                'direction': 'positive' if total_seconds >= 0 else 'negative'
            }), 200

        except (ValueError, OSError) as e:
            return jsonify({'error': f'时间格式错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timestamp_tools_bp.route('/add-time', methods=['POST'])
def add_time():
    """时间加法计算"""
    try:
        data = request.get_json()
        if not data or 'base_time' not in data:
            return jsonify({'error': '请提供base_time字段'}), 400

        base_time = data['base_time']
        additions = data.get('additions', [])
        time_type = data.get('type', 'timestamp')  # timestamp 或 datetime_string

        try:
            if time_type == 'datetime_string':
                format_string = data.get('format', '%Y-%m-%d %H:%M:%S')
                base_dt = datetime.datetime.strptime(base_time, format_string)
            else:
                base_dt = datetime.datetime.fromtimestamp(base_time)

            result_dt = base_dt
            operations = []

            # 依次添加时间
            for addition in additions:
                unit = addition.get('unit', 'days')
                amount = addition.get('amount', 1)

                if unit == 'years':
                    # 处理年份（考虑闰年）
                    result_dt = result_dt.replace(year=result_dt.year + amount)
                elif unit == 'months':
                    # 处理月份
                    new_month = result_dt.month + amount
                    new_year = result_dt.year + (new_month - 1) // 12
                    new_month = ((new_month - 1) % 12) + 1
                    result_dt = result_dt.replace(year=new_year, month=new_month)
                elif unit == 'weeks':
                    result_dt = result_dt + datetime.timedelta(weeks=amount)
                elif unit == 'days':
                    result_dt = result_dt + datetime.timedelta(days=amount)
                elif unit == 'hours':
                    result_dt = result_dt + datetime.timedelta(hours=amount)
                elif unit == 'minutes':
                    result_dt = result_dt + datetime.timedelta(minutes=amount)
                elif unit == 'seconds':
                    result_dt = result_dt + datetime.timedelta(seconds=amount)

                operations.append(f'+{amount} {unit}')

            return jsonify({
                'success': True,
                'original_time': base_time,
                'result_timestamp': int(result_dt.timestamp()),
                'result_datetime': result_dt.isoformat(),
                'operations': operations,
                'total_operations': len(operations)
            }), 200

        except (ValueError, OSError) as e:
            return jsonify({'error': f'时间格式错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timestamp_tools_bp.route('/business-days', methods=['POST'])
def calculate_business_days():
    """计算工作日"""
    try:
        data = request.get_json()
        if not data or 'start_date' not in data or 'end_date' not in data:
            return jsonify({'error': '请提供start_date和end_date字段'}), 400

        start_date_str = data['start_date']
        end_date_str = data['end_date']
        include_weekends = data.get('include_weekends', False)
        holidays = data.get('holidays', [])  # 节假日列表

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if start_date > end_date:
                return jsonify({'error': '开始日期不能晚于结束日期'}), 400

            business_days = 0
            current_date = start_date

            while current_date <= end_date:
                # 检查是否为工作日
                is_weekend = current_date.weekday() >= 5  # 0-4是周一到周五，5-6是周六日
                is_holiday = str(current_date) in holidays

                if not include_weekends:
                    if not is_weekend and not is_holiday:
                        business_days += 1
                else:
                    if not is_holiday:
                        business_days += 1

                current_date += datetime.timedelta(days=1)

            total_days = (end_date - start_date).days + 1
            weekend_days = sum(1 for d in range(total_days)
                              if (start_date + datetime.timedelta(days=d)).weekday() >= 5)

            return jsonify({
                'success': True,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'business_days': business_days,
                'total_days': total_days,
                'weekend_days': weekend_days,
                'holiday_days': len(holidays),
                'include_weekends': include_weekends
            }), 200

        except ValueError as e:
            return jsonify({'error': f'日期格式错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timestamp_tools_bp.route('/batch-calculate', methods=['POST'])
def batch_calculate():
    """批量时间计算"""
    try:
        data = request.get_json()
        if not data or 'base_times' not in data or 'operation' not in data:
            return jsonify({'error': '请提供base_times和operation字段'}), 400

        base_times = data['base_times']
        operation = data['operation']
        unit = data.get('unit', 'days')
        amount = data.get('amount', 1)
        time_type = data.get('type', 'timestamp')

        if not isinstance(base_times, list):
            return jsonify({'error': 'base_times必须是数组'}), 400

        results = []

        for i, base_time in enumerate(base_times):
            try:
                if time_type == 'datetime_string':
                    format_string = data.get('format', '%Y-%m-%d %H:%M:%S')
                    base_dt = datetime.datetime.strptime(base_time, format_string)
                else:
                    base_dt = datetime.datetime.fromtimestamp(base_time)

                # 执行计算
                if operation == 'add':
                    if unit == 'years':
                        result_dt = base_dt.replace(year=base_dt.year + amount)
                    elif unit == 'months':
                        new_month = base_dt.month + amount
                        new_year = base_dt.year + (new_month - 1) // 12
                        new_month = ((new_month - 1) % 12) + 1
                        result_dt = base_dt.replace(year=new_year, month=new_month)
                    elif unit == 'weeks':
                        result_dt = base_dt + datetime.timedelta(weeks=amount)
                    elif unit == 'days':
                        result_dt = base_dt + datetime.timedelta(days=amount)
                    elif unit == 'hours':
                        result_dt = base_dt + datetime.timedelta(hours=amount)
                    elif unit == 'minutes':
                        result_dt = base_dt + datetime.timedelta(minutes=amount)
                    elif unit == 'seconds':
                        result_dt = base_dt + datetime.timedelta(seconds=amount)
                    else:
                        result_dt = base_dt
                elif operation == 'subtract':
                    if unit == 'years':
                        result_dt = base_dt.replace(year=base_dt.year - amount)
                    elif unit == 'months':
                        new_month = base_dt.month - amount
                        new_year = base_dt.year + (new_month - 1) // 12
                        new_month = ((new_month - 1) % 12) + 1
                        result_dt = base_dt.replace(year=new_year, month=new_month)
                    elif unit == 'weeks':
                        result_dt = base_dt - datetime.timedelta(weeks=amount)
                    elif unit == 'days':
                        result_dt = base_dt - datetime.timedelta(days=amount)
                    elif unit == 'hours':
                        result_dt = base_dt - datetime.timedelta(hours=amount)
                    elif unit == 'minutes':
                        result_dt = base_dt - datetime.timedelta(minutes=amount)
                    elif unit == 'seconds':
                        result_dt = base_dt - datetime.timedelta(seconds=amount)
                    else:
                        result_dt = base_dt
                else:
                    result_dt = base_dt

                results.append({
                    'index': i,
                    'original': base_time,
                    'result_timestamp': int(result_dt.timestamp()),
                    'result_datetime': result_dt.isoformat(),
                    'operation': f'{operation} {amount} {unit}'
                })

            except Exception as e:
                results.append({
                    'index': i,
                    'original': base_time,
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'total': len(base_times),
            'successful': len([r for r in results if 'error' not in r]),
            'failed': len([r for r in results if 'error' in r]),
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _format_time_difference(time_diff):
    """格式化时间差为人类可读的字符串"""
    total_seconds = int(time_diff.total_seconds())
    if total_seconds == 0:
        return "0秒"

    parts = []
    if abs(total_seconds) >= 86400:  # 天
        days = abs(total_seconds) // 86400
        parts.append(f"{days}天")
        total_seconds %= 86400

    if abs(total_seconds) >= 3600:  # 小时
        hours = abs(total_seconds) // 3600
        parts.append(f"{hours}小时")
        total_seconds %= 3600

    if abs(total_seconds) >= 60:  # 分钟
        minutes = abs(total_seconds) // 60
        parts.append(f"{minutes}分钟")
        total_seconds %= 60

    if total_seconds > 0:  # 秒
        parts.append(f"{total_seconds}秒")

    result = "".join(parts)
    return result if time_diff.total_seconds() >= 0 else f"-{result}"

@timestamp_tools_bp.route('/formats', methods=['GET'])
def get_time_formats():
    """获取常用时间格式"""
    formats = {
        'ISO 8601': '%Y-%m-%dT%H:%M:%S',
        '本地时间': '%Y-%m-%d %H:%M:%S',
        '日期': '%Y-%m-%d',
        '时间': '%H:%M:%S',
        '美式日期': '%m/%d/%Y',
        '欧式日期': '%d/%m/%Y',
        '完整日期时间': '%A, %B %d, %Y %H:%M:%S',
        '日志格式': '%Y-%m-%d %H:%M:%S.%f',
        'UTC格式': '%Y-%m-%dT%H:%M:%SZ'
    }

    return jsonify({
        'success': True,
        'formats': formats
    }), 200
