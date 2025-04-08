from flask import render_template, Blueprint, flash, redirect, url_for,request
from flask_login import login_user, logout_user, login_required,current_user
from App.utils import send_email
from App import db
from sqlalchemy import or_
from App.models import User,Service,Booking,Review
from App.forms import RegistrationForm, LoginForm,ResetRequestForm,ResetPasswordForm,BookingForm,CancelBookingForm,AcceptOrderForm,AddServiceForm,SentOrderForm,CompleteOrderForm,ReviewForm
from datetime import datetime, UTC

main=Blueprint('main',__name__)
@main.route('/')
@main.route('/home')
def home_page():
    return render_template("home.html")


@main.route('/customer-dashboard')
@login_required
def customers_dashboard():
    return render_template('customer_dashboard.html')

@main.route('/provider-dashboard')
@login_required
def providers_dashboard():
    return render_template('provider_dashboard.html')



@main.route('/admin-dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')


@main.route('/register',methods=['GET','POST'])
def register_page():
    form=RegistrationForm()
    form.provided_services.choices = [(s.service_name, s.service_name) for s in Service.query.all()]
    if form.validate_on_submit():
        new_user=User(username=form.username.data,email_address=form.email_address.data,password=form.password.data,role=form.role.data)
        if new_user.role == 'Service Provider':
            new_user.set_provided_services(form.provided_services.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Account created successfully! You are now logged in",category="success")
        if form.role.data=='Customer':
            return redirect(url_for('main.customers_dashboard'))
        elif form.role.data == 'Service Provider':
            return redirect(url_for('main.providers_dashboard'))
        else:
            return redirect(url_for('main.admin_dashboard'))

    if form.errors!={}:
        for error in form.errors.values():
            flash(f"Error occur while registering: {error}",category='danger')

    return render_template("register.html",form=form)


@main.route('/login',methods=['GET','POST'])
def login_page():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email_address=form.email_address.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            user.last_login=datetime.now(UTC)
            db.session.commit()
            flash("You are logged in",category="success")
            if user.role=='Customer':
                return redirect(url_for('main.customers_dashboard'))
            elif user.role=='Service Provider':
                return redirect(url_for('main.providers_dashboard'))
            else:
                return redirect(url_for('main.admin_dashboard'))
        else:
            flash("Invalid username or password",category='danger')
            return redirect(url_for('main.login_page'))
    return render_template("login.html",form=form)

@main.route('/logout')
def logout_page():
    logout_user()
    flash("You are now logged out",category="info")
    return redirect(url_for('main.login_page'))

@main.route('/reset_password',methods=['GET','POST'])
def reset_request():
    form=ResetRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email_address=form.email_address.data).first()
        if user:
            send_email(user)
            flash("An email has been sent with instructions to reset your password",category="info")
            return redirect(url_for('main.login_page'))
        else:
            flash("No account found with that email",category='danger')
            return redirect(url_for('main.login_page'))
    return render_template("reset_request.html",form=form)

@main.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    user=User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token!",category='danger')
        return redirect(url_for('main.login_page'))

    form=ResetPasswordForm()
    if form.validate_on_submit():
        if user.verify_password(form.password.data):
            flash("Please enter a new password!",category='danger')
        else:
            user.password = form.password.data
            db.session.commit()
            flash("Your password has been updated! You are now able to log in",category='success')
            return redirect(url_for('main.login_page'))
    return render_template("reset_password.html",form=form)

@main.route('/book_service',methods=['GET','POST'])
def book_service_page():
    booking_form=BookingForm()
    cancelling_form=CancelBookingForm()
    if request.method=='POST':
        booked_service=request.form.get('book_service')
        b_obj=Service.query.filter_by(service_name=booked_service).first()
        if b_obj:
            exist_booking = Booking.query.filter(Booking.user_id == current_user.id, Booking.service_id == b_obj.id, or_(Booking.status == 'Pending', Booking.status == 'Accepted')).first()
            if exist_booking:
                flash("You already request for this service! Please try a new one", category='danger')
            else:
                new_booking=Booking(user_id=current_user.id,service_id=b_obj.id,status='Pending',address=booking_form.address.data)
                db.session.add(new_booking)
                db.session.commit()
                flash("Your request Has been received! Wait for confirmation",category='success')
        cancel_service=request.form.get('cancel_booking')
        c_obj=Service.query.filter_by(service_name=cancel_service).first()
        if c_obj:
            cancelled_booking = Booking.query.filter_by(user_id=current_user.id, service_id=c_obj.id).first()
            if cancelled_booking:
                db.session.delete(cancelled_booking)
                db.session.commit()
                flash("Your booking has been cancelled!",category='info')
            else:
                flash("Something went wrong! Try again later",category='danger')
        return redirect(url_for('main.book_service_page'))
    if request.method=='GET':
        services=Service.query.all()
        owned_bookings=Booking.query.filter_by(user_id=current_user.id,status='Pending').all()
        if owned_bookings:
            owned_services = [booking.service for booking in owned_bookings]
        else:
            owned_services = []
        return render_template('book_service.html',services=services,booking_form=booking_form,cancelling_form=cancelling_form,owned_services=owned_services)

    return redirect(url_for('main.book_service_page'))


@main.route('/manage_bookings',methods=['GET','POST'])
def manage_bookings_page():
    sending_order_form=SentOrderForm()
    if request.method=='POST':
        send_order=request.form.get('send_order')
        s_obj=Booking.query.filter_by(id=send_order).first()
        if s_obj:
            s_obj.status='Send'
            db.session.commit()
            flash("You have sent  the order to the providers!",category='info')
    if request.method=='GET':
        pending_orders=Booking.query.filter_by(status='Pending').all()
        accepted_orders=Booking.query.filter_by(status='Accepted').all()
        return render_template('manage_booking.html',sending_order_form=sending_order_form,pending_orders=pending_orders,bookings=accepted_orders)
    return redirect(url_for('main.manage_bookings_page'))

@main.route('/add_service',methods=['GET','POST'])
def add_service_page():
    form=AddServiceForm()
    if form.validate_on_submit():
        new_service = Service(service_name=form.service_name.data, description=form.description.data,category=form.category.data, price=form.price.data)
        db.session.add(new_service)
        db.session.commit()
        flash("Service added successfully!",category="success")
        return redirect(url_for('main.manage_bookings_page'))
    if form.errors!={}:
        for error in form.errors.values():
            flash(f"Error occur while adding new service: {error}",category='danger')

    return render_template("add_new_service.html",form=form)


@main.route('/all_bookings',methods=['GET','POST'])
def all_bookings_page():
    cancelling_form=CancelBookingForm()
    if request.method=='POST':
        cancel_booking= request.form.get('cancel_booking')
        cancelled_booking=Booking.query.filter_by(id=cancel_booking).first()
        if cancelled_booking:
            if current_user.rating>=0.5:
                current_user.rating-=0.5
            db.session.delete(cancelled_booking)
            db.session.commit()
            flash("Your booking has been cancelled!Your rating will be affected", category='warning')
        else:
            flash("Something went wrong! Try again later", category='danger')
        return redirect(url_for('main.all_bookings_page'))
    if request.method=='GET':
        all_accepted_bookings=Booking.query.filter_by(user_id=current_user.id, status='Accepted').all()
        return render_template('customer_all_bookings.html',bookings=all_accepted_bookings,cancelling_form=cancelling_form)
    return redirect(url_for('main.all_bookings_page'))

@main.route('/customer_booking_history',methods=['GET'])
def customer_booking_history():
    all_completed_bookings=Booking.query.filter_by(user_id=current_user.id, status='Completed').all()
    return render_template("customer_booking_history.html",bookings=all_completed_bookings)

@main.route('/provider_booking_orders',methods=['GET','POST'])
def provider_booking_orders_page():
    accepting_order_form = AcceptOrderForm()
    completed_order_form = CompleteOrderForm()
    all_accepted_bookings = Booking.query.filter_by(provider_id=current_user.id, status='Accepted').all()
    if request.method == 'POST':
        accepted_order = request.form.get('accept_order')
        a_obj = Booking.query.filter_by(id=accepted_order).first()
        if a_obj:
            if len(all_accepted_bookings) >= 2:
                flash("To accept new order, you have to complete previous orders.", category='danger')
                return redirect(url_for('main.providers_dashboard'))
            else:
                a_obj.status = 'Accepted'
                a_obj.Booking_Accept_date = datetime.now(UTC)
                a_obj.provider_id = current_user.id
                db.session.commit()
                flash('Order accepted successfully', 'success')

        completed_order = request.form.get('complete_order')
        c_obj = Booking.query.filter_by(id=completed_order).first()
        if c_obj:
            c_obj.status = 'Completed'
            c_obj.order_completed_date = datetime.now(UTC)
            user=User.query.filter_by(id= c_obj.user_id).first()
            if user.rating<=4.5:
                user.rating+=0.5
            db.session.commit()
            flash("You just complete the order", "success")

    if request.method == 'GET':
        all_new_orders = Booking.query.filter_by(status='Send').all()
        filtered_orders = [
            order for order in all_new_orders if order.service.service_name in current_user.provided_services
        ]
        return render_template('provider_orders.html', accepting_order_form=accepting_order_form,bookings=all_accepted_bookings, new_orders=filtered_orders,completed_order_form=completed_order_form)
    return redirect(url_for('main.provider_booking_orders_page'))
@main.route('/provider_booking_history',methods=['GET'])
def provider_booking_history():
    all_completed_orders=Booking.query.filter_by(provider_id=current_user.id, status='Completed').all()
    return render_template("provider_booking_history.html",bookings=all_completed_orders)

@main.route('/submit_review/<int:booking_id>', methods=['GET', 'POST'])
def submit_review(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    existing_review = Review.query.filter_by(user_id=current_user.id, booking_id=booking.id).first()

    if existing_review:
        flash('You have already reviewed this booking.', 'warning')
        return redirect(
            url_for('main.customer_booking_history'))  # Redirect to the booking history page or any appropriate page

    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(
            user_id=current_user.id,
            service_id=booking.service_id,
            rating=form.rating.data,
            booking_id=booking.id,
            review_text=form.review_text.data,
            review_date=datetime.now(UTC),
        )
        db.session.add(review)
        db.session.commit()

        service = Service.query.get(booking.service_id)
        all_service_reviews = Review.query.filter_by(service_id=service.id).all()

        if all_service_reviews:
            avg_rating = sum(r.rating for r in all_service_reviews) / len(all_service_reviews)
            service.rating = round(avg_rating,1)
            db.session.commit()

        provider_id = booking.provider_id
        provider = User.query.filter_by(id=provider_id, role='Service Provider').first()
        if provider:
            provider_reviews = (
                Review.query
                .join(Booking, Review.booking_id == Booking.id)
                .filter(Booking.provider_id == provider.id)
                .all()
            )
            if provider_reviews:
                avg_provider_rating = sum(r.rating for r in provider_reviews) / len(provider_reviews)
                provider.rating = round(avg_provider_rating, 1)

        db.session.commit()

        flash('Your review has been submitted successfully!', 'success')
        return redirect(url_for('main.customer_booking_history'))

    return render_template('review.html', form=form, booking=booking)


@main.route('/provider_reviews',methods=['GET'])
def provider_reviews_page():
    filtered_reviews=[]
    all_completed_orders = Booking.query.filter_by(provider_id=current_user.id, status='Completed').all()
    all_reviews=Review.query.all()
    for review in all_reviews:
        for order in all_completed_orders:
            if review.booking_id==order.id:
                filtered_reviews.append(review)
    print(filtered_reviews)

    return render_template('provider_reviews.html',reviews=filtered_reviews)


@main.route('/coming_soon')
def coming_soon():
    return render_template('coming_soon.html')

