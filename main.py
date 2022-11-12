import shutil

import requests

from database import TableDba, create_db, TableModel, AccountDba, Account
from certificate import Blockchain
import streamlit as st
from streamlit_option_menu import option_menu
from ipfs_api import IPFSApi
# import streamlit_authenticator as stauth
import pandas as pd
import cv2 as cv
import ipfsApi
import os
import json

authentication_status = True

from tronpy import Tron
from tronpy.keys import PrivateKey

# integers representing half & one Tron
HALF_TRON = 500000
ONE_TRON = 1000000

# your wallet information
WALLET_ADDRESS = "TP59LgebV1VtQMswGiju9PEYZ4dT3ziNHa"
PRIVATE_KEY = "fb001bcc4f82c6260b21f00faa400b34630ea796e72c9c4f2fc99216a6e8085a"

# connect to the Tron blockchain
client = Tron(network='nile')

# send some 'amount' of Tron to the 'wallet' address
def send_tron(amount, wallet):
    try:
        priv_key = PrivateKey(bytes.fromhex(PRIVATE_KEY))
        
        # create transaction and broadcast it
        txn = (
            client.trx.transfer(WALLET_ADDRESS, str(wallet), int(amount))
            .memo("Transaction Description")
            .build()
            .inspect()
            .sign(priv_key)
            .broadcast()
        )
        # wait until the transaction is sent through and then return the details  
        return txn.wait()

    # return the exception
    except Exception as ex:
        return ex



def process_file():
    st.title("Upload XLSX with list of names")
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        api = ipfsapi.Client(host='https://ipfs.infura.io', port=5001)
        block = Blockchain()
        block.mine_block()
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'output')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

        template_path = 'template_certificate.png'
        output_path = 'output/'

        font_size = 3
        font_color = (0, 0, 0)

        coordinate_y_adjustment = -30
        coordinate_x_adjustment = 10
        st.subheader("fedup")

        df = pd.read_excel(uploaded_file, engine='openpyxl')
        names = df['Name'].tolist()
        contracts= df['Contract'].tolist()
        st.dataframe(df['Contract'])
        
        recipient_address = df.iat[0, 1]
        st.text("Hello")

        amount = 1000000
        k=send_tron(amount,recipient_address)
        st.text(k)
        
        
        block=pd.DataFrame(d, columns=('HashBlock'))
        st.dataframe(block)
        st.dataframe(df)
        for i in names:
            proof = block.get_previous_hash()
            certi_name = i
            block.add_transaction(proof)

            img = cv.imread(template_path)

            font = cv.FONT_HERSHEY_PLAIN

            text_size = cv.getTextSize(certi_name, font, font_size, 10)[0]
            text_x = (img.shape[1] - text_size[0]) / 2 + coordinate_x_adjustment
            text_y = (img.shape[0] + text_size[1]) / 2 - coordinate_y_adjustment
            text_x = int(text_x)
            text_y = int(text_y)

            cv.putText(img, certi_name, (text_x, text_y), font, font_size, font_color, 2)
            cv.putText(img, proof, (190, 680), font, 1, font_color, 2)

            certi_path = output_path + certi_name + '.png'

            status = cv.imwrite(f'output/{certi_name}.png', img)
            res = ipfs.ipfs_add(f'output/{certi_name}.png')
            block.add_transaction(res)
            block.mine_block()

        data = block.get_chain()
        table_values = []
        for i in data['chain']:
            if i['transactions'] is not None:
                try:
                    val = i['transactions'][1][0]
                    tx_hash = i['transactions'][0]
                    table_values.append({'name': val['Name'], 'ipfs_hash': val['Hash'], "tx_hash": tx_hash})
                    dynamic_model = TableModel()
                    dba = TableDba(model=dynamic_model)
                    dynamic_model.name = val['Name'].split('/')[-1].split('.')[0]
                    dynamic_model.ipfs_hash = val['Hash']
                    dynamic_model.block_chain_hash = tx_hash
                   # dynamic_model.tron_hash = k['id']
                    result = dba.add_entry(dynamic_model)
                    print(result)
                except Exception as e:
                    pass
        st.subheader("Generated_Certificates_Table")
        st.dataframe(df)
        st.dataframe(pd.DataFrame(table_values))
        shutil.make_archive('output/', 'zip', 'output/')
        with open("output.zip", "rb") as fp:
            btn = st.download_button(
                label="Download ZIP",
                data=fp,
                file_name="output.zip",
                mime="application/zip"
            )

        dir = 'output/'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
    if st.button('clear all data'):
        dynamic_model = TableModel()
        dba = TableDba(model=dynamic_model)
        ret = dba.delete_all()
        st.write('Database clear now')


# 1. as sidebar menu

selected = option_menu("Certificate Validation", ["Home", 'Check'],
                       icons=['house', 'gear'], menu_icon="cast", default_index=1, orientation="horizontal")
create_db()
acc_dba = AccountDba()
# print('default account')
acc_dba.add_default_account()
ipfs = IPFSApi()


def authentication():
    # t = st.empty()
    # login_form = t.form('Login')
    # login_form.subheader('Login')
    # input_username = login_form.text_input('Username')
    # input_password = login_form.text_input('Password', type='password')
    # if login_form.form_submit_button('Login'):
    #     # global authentication_status
    #     print('us', input_username)
    #     res = acc_dba.get_by_user_name(input_username)
    #     if res:
    #         if res[0].get('password') == input_password:
    #             authentication_status = True
    #         else:
    #             authentication_status = False
    res = acc_dba.get_by_user_name('Admin')
    username = []
    password = []
    names = ['Admin']
    username.append(res[0]['user_name'])
    password.append(res[0]['password'])
    login_form = st.form('Login')
    login_form.subheader('Login')
    input_username = login_form.text_input('Username')
    input_password = login_form.text_input('Password', type='password')
    if login_form.form_submit_button('Login'):
        global authentication_status
        res = acc_dba.get_by_user_name(input_username)
        if res:
            if res[0].get('password') == input_password:
                authentication_status = True
            else:
                authentication_status = False


if selected == "Home":
    # authentication_status = authentication()
    if authentication_status:
        st.title("Upload XLSX with list of names")
        uploaded_file = st.file_uploader("Choose a file")
        
        if uploaded_file is not None:
            block = Blockchain()
            block.mine_block()
            current_directory = os.getcwd()
            final_directory = os.path.join(current_directory, r'output')
            if not os.path.exists(final_directory):
                os.makedirs(final_directory)

            template_path = 'template_certificate.png'
            output_path = 'output/'

            font_size = 3
            font_color = (0, 0, 0)

            coordinate_y_adjustment = -30
            coordinate_x_adjustment = 10

            df = pd.read_excel(uploaded_file, engine='openpyxl')
            names = df['Name'].tolist()


            contracts= df['Contract'].tolist()
            st.dataframe(df['Contract'])

            recipient_address = df.iat[0, 1]
            
            sam=st.empty()
            sam.markdown('**Connecting to Tron Network**')
            sam.markdown('**Initalizing the Transfer of funds**')
            sam.markdown('**Transferring Tron Tokens to **',df.iat[0, 1])

            amount = 1000000
            k=send_tron(amount,recipient_address)
            sam.success('**Transaction Successful**')
            sam.empty()
    
            st.text(k)
            st.success('**Tron HashID**',k['id'])
            
            
            st.dataframe(df)
            for i in names:
                proof = block.get_previous_hash()
                certi_name = i
                block.add_transaction(proof)

                img = cv.imread(template_path)

                font = cv.FONT_HERSHEY_PLAIN

                text_size = cv.getTextSize(certi_name, font, font_size, 10)[0]
                text_x = (img.shape[1] - text_size[0]) / 2 + coordinate_x_adjustment
                text_y = (img.shape[0] + text_size[1]) / 2 - coordinate_y_adjustment
                text_x = int(text_x)
                text_y = int(text_y)

                cv.putText(img, certi_name, (text_x, text_y), font, font_size, font_color, 2)
                cv.putText(img, proof, (190, 680), font, 1, font_color, 2)

                certi_path = output_path + certi_name + '.png'

                status = cv.imwrite(f'output/{certi_name}.png', img)
                print(certi_path)
                res = ipfs.nft_storage_store(certi_path)
                res = {'Hash': res['value']['cid'], 'Name': f'output/{certi_name}.png'}
                block.add_transaction(res)
                block.mine_block()

            data = block.get_chain()
            table_values = []
            for i in data['chain']:
                if i['transactions']:
                    try:
                        val = i['transactions'][1]
                        tx_hash = i['transactions'][0]
                        table_values.append({'name': val['Name'], 'ipfs_cid': val['Hash'], "tx_hash": tx_hash})
                        dynamic_model = TableModel()
                        dba = TableDba(model=dynamic_model)
                        dynamic_model.name = val['Name'].split('/')[-1].split('.')[0]
                        dynamic_model.ipfs_hash = val['Hash']
                        dynamic_model.block_chain_hash = tx_hash
                        result = dba.add_entry(dynamic_model)
                    except Exception as e:
                        pass
            st.subheader("Generated_Certificates_Table")
            
            st.dataframe(pd.DataFrame(table_values))
            shutil.make_archive('output/', 'zip', 'output/')
            with open("output.zip", "rb") as fp:
                btn = st.download_button(
                    label="Download ZIP",
                    data=fp,
                    file_name="output.zip",
                    mime="application/zip"
                )

            dir = 'output/'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
        if st.button('clear all data'):
            dynamic_model = TableModel()
            dba = TableDba(model=dynamic_model)
            ret = dba.delete_all()
            st.write('Database clear now')
    elif authentication_status == False:
        st.error('Username / password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')
    # if st.button('Logout'):
    #     st.session_state.authentication_status = False

if selected == "Check":
    name = st.text_input('Enter the Name')
    record_date = st.date_input('Select Date')
    wallet_address = None
    if st.checkbox('MINT AS NFT'):
        wallet_address = st.text_area('Wallet Address')

    if st.button('search'):
        dynamic_model = TableModel()
        dba = TableDba(model=dynamic_model)
        ret = dba.get(name=name, record_date=record_date)
        record = ret.get('data')
        if len(record):
            ipfs_url = ipfs.ipfs_get(record)
            if wallet_address:
                res_data = ipfs.nft_port_minting(record, wallet_address, ipfs_url)
                if res_data:
                    file = 'tmp/{}.png'.format(record[0].get('ipfs_hash'))
                    store_nft = ipfs.nft_storage_store(file)
                    st.subheader("Retrive Stored image Data from NFT Storage")
                    st.write(store_nft)
                    st.markdown("#")
                    st.subheader("Minted Image")
                    image_cid = store_nft['value']['cid']
                    st.write(f'https://{image_cid}.ipfs.nftstorage.link/')
                    if store_nft:
                        meta_file = 'tmp/temp_{}.json'.format(image_cid)
                        with open(meta_file,'w+') as f:
                            json.dump(res_data,f)
                        nft_meta = ipfs.nft_storage_store(meta_file)
                        st.markdown("#")
                        st.subheader("Retrive Stored Meta Data from NFT Storage")
                        retrive_data = ipfs.get_nft_storage(nft_meta['value']['cid'])
                        st.success(retrive_data)
                        meta_cid = retrive_data['value']['cid']
                        st.markdown("#")
                        st.write(f'https://{meta_cid}.ipfs.nftstorage.link/')
                        meta_d = requests.get(url=f'https://{meta_cid}.ipfs.nftstorage.link/')
                        temp = json.loads(meta_d.content.decode('utf-8'))
                        new_dict = {key: val for key,
                                                 val in temp.items() if
                                    key not in ['name', 'description', 'file_url', 'response']}
                        st.json(new_dict)

        else:
            st.write('No record found')

